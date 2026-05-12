const ADS_ENABLED=false;
const AD_SLOTS={bannerTop:{desktop:'',mobile:''},resultBelow:{desktop:'',mobile:''},contentMid:{desktop:'',mobile:''},sidebar:{desktop:'',mobile:''},contentEnd:{desktop:'',mobile:''},footer:{desktop:'',mobile:''}};
function isMobile(){return window.innerWidth<768}
function renderAd(s,c){if(!ADS_ENABLED)return;const el=document.getElementById(c);if(!el)return;const h=isMobile()?AD_SLOTS[s].mobile:AD_SLOTS[s].desktop;if(h)el.innerHTML=h}
document.addEventListener('DOMContentLoaded',function(){['bannerTop','resultBelow','contentMid','sidebar','contentEnd','footer'].forEach(function(s,i){renderAd(s,['ad-banner-top','ad-result-below','ad-content-mid','ad-sidebar','ad-content-end','ad-footer-bottom'][i]);});});