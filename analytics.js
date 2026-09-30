window.dataLayer = window.dataLayer || [];
function gtag() {
  dataLayer.push(arguments);
}
gtag('js', new Date());
// Local previews stay out of the reports.
if (location.hostname === 'maps.jianart.com') gtag('config', 'G-9888HFYBES');
