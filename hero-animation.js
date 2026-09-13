// Choreograph the hero wordmark, then dock it as the permanent corner logo.
(() => {
  const hero=document.querySelector(".hero");
  const wordmark=hero?.querySelector(".hero-wordmark");
  const svg=wordmark?.querySelector("svg");
  if(!hero||!wordmark||!svg)return;

  const order=["V","S","p","a","c","e"];
  const moon=svg.querySelector('[data-part="moon"] text');
  const letters=order.map(id=>svg.querySelector(`[data-part="${id}"]`));
  if(!moon||letters.some(part=>!part))return;

  const nativeMoon=moon.textContent;
  const reduced=window.matchMedia("(prefers-reduced-motion: reduce)");

  // Animate parents, never overwrite native rig transforms.
  const wrappers=letters.map(part=>{
    const wrapper=document.createElementNS("http://www.w3.org/2000/svg","g");
    wrapper.classList.add("hero-arrival");
    part.before(wrapper);
    wrapper.append(part);
    return wrapper;
  });

  const journeys=[
    {delay:0,duration:1850,easing:"cubic-bezier(.22,.7,.2,1)",frames:[
      {transform:"translate(-150px,-65px) rotate(-22deg) scale(.82)",opacity:0},
      {offset:.58,transform:"translate(-36px,24px) rotate(9deg) scale(1.04)",opacity:1},
      {offset:.84,transform:"translate(7px,-4px) rotate(-3deg) scale(1.01)",opacity:1}]},
    {delay:400,duration:1500,easing:"cubic-bezier(.2,.6,.3,1)",frames:[
      {transform:"translate(115px,-110px) rotate(32deg) scale(.7)",opacity:0},
      {offset:.48,transform:"translate(45px,-45px) rotate(-13deg) scale(.95)",opacity:1},
      {offset:.78,transform:"translate(-12px,12px) rotate(7deg) scale(1.06)",opacity:1}]},
    {delay:800,duration:1400,easing:"cubic-bezier(.16,.8,.3,1)",frames:[
      {transform:"translate(-24px,125px) rotate(17deg) scale(.6)",opacity:0},
      {offset:.6,transform:"translate(17px,-20px) rotate(-11deg) scale(1.08)",opacity:1},
      {offset:.85,transform:"translate(-4px,5px) rotate(3deg) scale(.98)",opacity:1}]},
    {delay:1200,duration:1650,easing:"cubic-bezier(.3,.5,.15,1)",frames:[
      {transform:"translate(155px,34px) rotate(-48deg) scale(1.2)",opacity:0},
      {offset:.5,transform:"translate(44px,-32px) rotate(20deg) scale(.87)",opacity:1},
      {offset:.8,transform:"translate(-8px,-7px) rotate(-5deg) scale(1.03)",opacity:1}]},
    {delay:1600,duration:1750,easing:"cubic-bezier(.25,.65,.35,1)",frames:[
      {transform:"translate(-85px,-105px) rotate(-65deg) scale(.75)",opacity:0},
      {offset:.38,transform:"translate(-60px,-35px) rotate(-25deg) scale(.92)",opacity:1},
      {offset:.7,transform:"translate(19px,17px) rotate(14deg) scale(1.05)",opacity:1},
      {offset:.9,transform:"translate(3px,-6px) rotate(-4deg) scale(1)",opacity:1}]},
    {delay:2000,duration:1450,easing:"cubic-bezier(.18,.7,.25,1)",frames:[
      {transform:"translate(85px,95px) rotate(55deg) scale(.5)",opacity:0},
      {offset:.52,transform:"translate(-18px,28px) rotate(-17deg) scale(1.12)",opacity:1},
      {offset:.82,transform:"translate(6px,-8px) rotate(6deg) scale(.96)",opacity:1}]}
  ];

  const phases=["🌕","🌖","🌗","🌘","🌑","🌒","🌓","🌔"];
  const timers=new Set();
  const animations=new Set();
  let generation=0;

  function later(callback,delay,run){
    const timer=setTimeout(()=>{
      timers.delete(timer);
      if(run===generation)callback();
    },delay);
    timers.add(timer);
  }

  function dock(run,animate=true){
    if(run!==generation)return;

    moon.textContent=nativeMoon;
    hero.classList.add("hero-docking");

    if(!animate){
      wordmark.classList.add("hero-wordmark--docked");
      hero.classList.add("hero-complete");
      return;
    }

    const start=wordmark.getBoundingClientRect();

    wordmark.classList.add("hero-wordmark--docked");

    const end=wordmark.getBoundingClientRect();
    const sx=start.width/end.width;
    const sy=start.height/end.height;
    const tx=start.left-end.left;
    const ty=start.top-end.top;

    const animation=wordmark.animate([
      {
        transform:`translate(${tx}px,${ty}px) scale(${sx},${sy})`
      },
      {
        transform:"translate(0px,0px) scale(1,1)"
      }
    ],{
      duration:900,
      easing:"cubic-bezier(.22,.8,.2,1)",
      fill:"both"
    });

    animations.add(animation);

    animation.finished.then(()=>{
      if(run!==generation)return;
      animation.cancel();
      animations.delete(animation);
      hero.classList.add("hero-complete");
    },()=>{});
  }

  function arrive(run){
    moon.textContent=nativeMoon;
    journeys.forEach((journey,index)=>later(()=>{
      const animation=wrappers[index].animate([
        ...journey.frames,
        {transform:"translate(0px,0px) rotate(0deg) scale(1)",opacity:1}
      ],{
        duration:journey.duration,
        easing:journey.easing,
        fill:"forwards"
      });

      animations.add(animation);

      animation.finished.then(()=>{
        if(run!==generation)return;

        wrappers[index].removeAttribute("style");
        animation.cancel();
        animations.delete(animation);

      },()=>{});
    },journey.delay,run));

    // Longest letter journey ends at 3.45s.
    // Hold the complete wordmark for 1 second, then dock it.
    later(()=>dock(run,true),4450,run);
  }

  function play(){
    ++generation;
    const run=generation;

    timers.forEach(clearTimeout);
    timers.clear();

    animations.forEach(animation=>animation.cancel());
    animations.clear();

    wrappers.forEach(wrapper=>{
      wrapper.removeAttribute("style");
      wrapper.style.opacity="0";
    });

    if(reduced.matches){
      wrappers.forEach(wrapper=>wrapper.removeAttribute("style"));
      moon.textContent=nativeMoon;
      dock(run,false);
      return;
    }

    moon.textContent=phases[0];

    let step=0;

    function advance(){
      if(++step===phases.length){
        arrive(run);
        return;
      }

      moon.textContent=phases[step];
      later(advance,180,run);
    }

    later(advance,180,run);
  }

  play();

  window.addEventListener("pagehide",()=>{
    ++generation;
    timers.forEach(clearTimeout);
    timers.clear();
    animations.forEach(animation=>animation.cancel());
    animations.clear();
  });
})();
