from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .alpaca_client import AlpacaGateway
from .backtest import run_sma_backtest
from .config import settings
from .storage import Storage
from .strategy import sma_trend_signal

storage = Storage(settings.database_path)
_runtime: dict[str, Any] = {"last_bar": None, "last_error": None}


async def _hourly_loop() -> None:
    if not settings.alpaca_configured:
        return
    gateway = AlpacaGateway(settings)
    while True:
        try:
            bars = await asyncio.to_thread(gateway.hourly_bars, settings.symbol, 30)
            if not bars.empty:
                latest_bar = str(bars.iloc[-1]["timestamp"])
                if latest_bar != _runtime["last_bar"]:
                    result = sma_trend_signal(bars)
                    storage.save_decision(settings.symbol, result)
                    _runtime["last_bar"] = latest_bar
            _runtime["last_error"] = None
        except Exception as exc:  # keep the service alive; surface the error in the dashboard
            _runtime["last_error"] = str(exc)
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_hourly_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="MarketLoop", version="0.1.0", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return DASHBOARD_HTML


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True,
        "alpaca_configured": settings.alpaca_configured,
        "symbol": settings.symbol,
        "data_feed": settings.data_feed,
        "last_bar": _runtime["last_bar"],
        "last_error": _runtime["last_error"],
        "mode": "paper-readonly-dashboard",
    }


@app.get("/api/status")
def status() -> dict:
    if not settings.alpaca_configured:
        return {"configured": False, "message": "Add Alpaca paper API keys to .env on the host computer."}

    gateway = AlpacaGateway(settings)
    bars = gateway.hourly_bars(settings.symbol, 30)
    if bars.empty:
        return {"configured": True, "message": "No bars returned."}

    signal = sma_trend_signal(bars)
    account = gateway.paper_account()
    latest = bars.iloc[-1]
    recent = storage.recent_decisions(12)
    closes = [round(float(v), 4) for v in bars["close"].tail(48).tolist()]

    return {
        "configured": True,
        "symbol": settings.symbol,
        "latest_bar": str(latest["timestamp"]),
        "close": round(signal.close, 4),
        "signal": signal.signal,
        "sma_fast": round(signal.sma_fast, 4) if signal.sma_fast is not None else None,
        "sma_slow": round(signal.sma_slow, 4) if signal.sma_slow is not None else None,
        "reason": signal.reason,
        "account": account,
        "recent_decisions": recent,
        "closes": closes,
        "last_error": _runtime["last_error"],
    }


@app.get("/api/backtest")
def backtest(days: int = 365, cash: float = 100_000.0) -> dict:
    days = max(30, min(days, 3650))
    cash = max(100.0, min(cash, 100_000_000.0))
    if not settings.alpaca_configured:
        return {"configured": False, "message": "Alpaca paper API keys are required."}
    gateway = AlpacaGateway(settings)
    bars = gateway.hourly_bars(settings.symbol, days)
    result = run_sma_backtest(bars, initial_cash=cash)
    return {"configured": True, "symbol": settings.symbol, "days_requested": days, **result.as_dict()}


DASHBOARD_HTML = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
<title>MarketLoop</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#171717;background:#f5f5f2}
*{box-sizing:border-box} body{margin:0} .wrap{max-width:980px;margin:auto;padding:18px 14px 48px}.top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:8px 0 18px}.brand{font-weight:800;font-size:22px;letter-spacing:-.03em}.sub{font-size:12px;color:#737373}.badge{border:1px solid #d4d4d4;border-radius:999px;padding:7px 10px;font-size:12px;background:white}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.card{background:white;border:1px solid #e5e5e5;border-radius:18px;padding:16px;box-shadow:0 1px 2px rgba(0,0,0,.03)}.label{font-size:12px;color:#737373}.value{font-size:24px;font-weight:750;margin-top:6px;letter-spacing:-.03em}.section{margin-top:12px}.row{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid #eee;font-size:13px}.row:last-child{border:0}.signal{font-size:32px;font-weight:850;letter-spacing:-.04em}.buy{color:#16794b}.sell{color:#b42318}.hold{color:#5f5f5f}button{border:0;background:#171717;color:white;border-radius:12px;padding:11px 14px;font-weight:700;cursor:pointer}.actions{display:flex;gap:8px;align-items:center}.chart{width:100%;height:150px;margin-top:12px}.err{color:#b42318;font-size:13px;white-space:pre-wrap}.muted{color:#737373}.two{display:grid;grid-template-columns:1.1fr .9fr;gap:10px}@media(max-width:720px){.grid{grid-template-columns:repeat(2,1fr)}.two{grid-template-columns:1fr}.value{font-size:21px}.wrap{padding-top:10px}.top{align-items:flex-start}.actions{flex-direction:column;align-items:flex-end}}
</style>
</head>
<body><main class="wrap">
<div class="top"><div><div class="brand">MarketLoop</div><div class="sub">Tailscale-friendly · Alpaca Paper · 읽기 전용 모바일 대시보드</div></div><div class="actions"><span class="badge" id="conn">연결 확인 중</span><button onclick="loadAll()">새로고침</button></div></div>
<div class="grid">
<div class="card"><div class="label">종목</div><div class="value" id="symbol">-</div></div>
<div class="card"><div class="label">최근 종가</div><div class="value" id="price">-</div></div>
<div class="card"><div class="label">현재 판단</div><div class="value signal hold" id="signal">-</div></div>
<div class="card"><div class="label">Paper Equity</div><div class="value" id="equity">-</div></div>
</div>
<div class="two section">
<section class="card"><div class="label">최근 1시간봉</div><svg class="chart" viewBox="0 0 800 150" preserveAspectRatio="none" id="chart"></svg><div class="sub" id="barTime"></div></section>
<section class="card"><div class="label">판단 근거</div><div style="margin-top:10px;font-weight:650" id="reason">-</div><div class="row"><span>SMA20</span><b id="fast">-</b></div><div class="row"><span>SMA50</span><b id="slow">-</b></div><div class="row"><span>Buying Power</span><b id="bp">-</b></div></section>
</div>
<div class="two section">
<section class="card"><div class="label">최근 판단 기록</div><div id="history"><div class="muted" style="margin-top:10px">기록 없음</div></div></section>
<section class="card"><div class="label">기준 전략 백테스트</div><div class="row"><span>전략 수익률</span><b id="btReturn">-</b></div><div class="row"><span>Buy & Hold</span><b id="btHold">-</b></div><div class="row"><span>최대 낙폭</span><b id="btMdd">-</b></div><div class="row"><span>체결 횟수</span><b id="btTrades">-</b></div><div style="margin-top:10px"><button onclick="loadBacktest()">365일 백테스트</button></div></section>
</div>
<div class="section err" id="error"></div>
</main>
<script>
const money=n=>n==null?'-':Number(n).toLocaleString(undefined,{maximumFractionDigits:2});
function draw(vals){const s=document.getElementById('chart');s.innerHTML='';if(!vals||vals.length<2)return;const w=800,h=150,min=Math.min(...vals),max=Math.max(...vals),d=(max-min)||1;const pts=vals.map((v,i)=>`${i*w/(vals.length-1)},${h-8-(v-min)/d*(h-16)}`).join(' ');const p=document.createElementNS('http://www.w3.org/2000/svg','polyline');p.setAttribute('points',pts);p.setAttribute('fill','none');p.setAttribute('stroke','currentColor');p.setAttribute('stroke-width','3');p.setAttribute('vector-effect','non-scaling-stroke');s.appendChild(p)}
async function loadStatus(){try{const r=await fetch('/api/status');const d=await r.json();document.getElementById('conn').textContent=d.configured?'Alpaca 연결됨':'설정 필요';if(!d.configured){document.getElementById('error').textContent=d.message||'';return}document.getElementById('error').textContent=d.last_error||'';symbol.textContent=d.symbol;price.textContent='$'+money(d.close);signal.textContent=d.signal;signal.className='value signal '+d.signal.toLowerCase();equity.textContent='$'+money(d.account.equity);reason.textContent=d.reason;fast.textContent=money(d.sma_fast);slow.textContent=money(d.sma_slow);bp.textContent='$'+money(d.account.buying_power);barTime.textContent='최근 확정 봉: '+d.latest_bar;draw(d.closes);history.innerHTML=(d.recent_decisions||[]).map(x=>`<div class="row"><span>${x.signal} · $${money(x.close)}</span><span class="muted">${new Date(x.created_at).toLocaleString()}</span></div>`).join('')||'<div class="muted" style="margin-top:10px">기록 없음</div>'}catch(e){error.textContent=String(e)}}
async function loadBacktest(){try{const r=await fetch('/api/backtest?days=365&cash=100000');const d=await r.json();if(!d.configured){error.textContent=d.message;return}btReturn.textContent=d.return_pct+'%';btHold.textContent=d.buy_hold_pct+'%';btMdd.textContent=d.max_drawdown_pct+'%';btTrades.textContent=d.trades}catch(e){error.textContent=String(e)}}
function loadAll(){loadStatus()} loadAll(); setInterval(loadStatus,60000);
</script></body></html>'''
