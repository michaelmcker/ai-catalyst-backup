(() => {
  if (!['aicatalyst.biz', 'www.aicatalyst.biz'].includes(location.hostname)) return;
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('consent', 'default', {analytics_storage:'denied', ad_storage:'denied', ad_user_data:'denied', ad_personalization:'denied'});
  gtag('set', 'url_passthrough', false);
  gtag('js', new Date());
  gtag('config', 'G-YWZYZKJV9J', {allow_google_signals:false, allow_ad_personalization_signals:false, page_location:location.origin + location.pathname});
  const script=document.createElement('script');
  script.async=true;
  script.src='https://www.googletagmanager.com/gtag/js?id=G-YWZYZKJV9J';
  document.head.appendChild(script);
})();
