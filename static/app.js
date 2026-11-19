const tg=window.Telegram?.WebApp;tg?.ready();tg?.expand();
const initData=tg?.initData||"", $=id=>document.getElementById(id);
const headers={"Content-Type":"application/json","X-Telegram-Init-Data":initData};
let sessionId=null,timerId=null,remaining=15,locked=false;
function show(id){document.querySelectorAll(".screen").forEach(x=>x.classList.remove("active"));$(id).classList.add("active");$("error").classList.add("hidden");}
function showError(msg){$("error").textContent=msg;$("error").classList.remove("hidden");}
async function post(path,data={}){const r=await fetch(path,{method:"POST",headers,body:JSON.stringify(data)});if(!r.ok)throw new Error(await r.text());return r.json();}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
async function loadHome(){try{const me=await post("/api/me");$("best").textContent=me.best_score+"/50";$("games").textContent=me.games;
const r=await fetch("/api/leaderboard",{headers});if(!r.ok)throw Error();const d=await r.json();
$("leaderRows").innerHTML=d.leaders.length?d.leaders.map(x=>`<div class="leader-row"><span class="rank">${String(x.rank).padStart(2,"0")}</span><span class="leader-name">${esc(x.name)}</span><b class="leader-score">${x.score}/50</b></div>`).join(""):'<div class="muted">Пока нет завершённых игр. Стань первым!</div>';
}catch(e){$("leaderRows").textContent="Открой игру через Telegram, чтобы увидеть рейтинг.";}}
function stopTimer(){if(timerId)clearInterval(timerId);timerId=null;}
function startTimer(){stopTimer();remaining=15;$("timer").textContent=remaining;timerId=setInterval(()=>{remaining--;$("timer").textContent=remaining;if(remaining<=0){stopTimer();answer(-1,true);}},1000);}
function renderQuestion(q){locked=false;$("progress").textContent=`ВОПРОС ${q.position} / ${q.total}`;$("score").textContent=`СЧЁТ: ${q.score}`;$("bar").style.width=`${(q.position-1)/50*100}%`;$("topic").textContent=q.topic;$("question").textContent=q.question;
const letters=["A","B","C","D"];$("answers").innerHTML=q.options.map((v,i)=>`<button class="answer" data-i="${i}"><span class="letter">${letters[i]}</span><span>${esc(v)}</span></button>`).join("");
document.querySelectorAll(".answer").forEach(b=>b.addEventListener("click",()=>answer(Number(b.dataset.i),false)));startTimer();}
async function answer(index,timeout){if(locked)return;locked=true;stopTimer();document.querySelectorAll(".answer").forEach(b=>b.disabled=true);
try{const d=await post("/api/answer",{session_id:sessionId,answer:index});if(d.status==="playing"){renderQuestion(d.question);return;}finish(d.score,d.best_score,d.status);}
catch(e){locked=false;showError("Не удалось отправить ответ. Проверь соединение и попробуй снова.");}}
function finish(score,best,status){stopTimer();$("finalScore").textContent=score;$("finalBest").textContent=best;
$("resultTitle").innerHTML=score>=40?"ВЕЛИКОЛЕПНО<br><span>ТВОЙ УМ СИЛЁН</span>":score>=20?"ХОРОШАЯ<br><span>ПОПЫТКА</span>":"ЕСТЬ КУДА<br><span>РАСТИ</span>";
$("resultMessage").textContent=status==="won"?"Невероятно! Ты ответил правильно на все 50 вопросов.":status==="timeout"?"Время вышло. Следующая попытка может стать рекордной.":"Одна ошибка завершила игру. Попробуй ещё раз!";
show("result");}
async function startGame(){try{$("startBtn").disabled=true;const d=await post("/api/start");sessionId=d.session_id;show("game");renderQuestion(d.question);}catch(e){showError("Не удалось начать игру. Убедись, что открыл BRAINSIR через Telegram.");}finally{$("startBtn").disabled=false;}}
$("startBtn").addEventListener("click",startGame);$("againBtn").addEventListener("click",startGame);$("homeBtn").addEventListener("click",()=>{show("home");loadHome();});
loadHome();
