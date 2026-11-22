// Real-user metrics for https://idle-ti.me/performance/.
//
// Google's web-vitals library measures the page's Core Web Vitals (LCP, INP,
// CLS) plus FCP and TTFB. When the page is hidden or left, they leave in one
// beacon whose data is the URL path itself:
//
//   /rum/1/p=%2Fblog%2Fslug%2F;n=navigate;d=m;lcp=1234;cls=0.012;...
//
// A CloudFront Function answers it with an empty 204 and CloudFront's access
// log records the path; scripts/field_data.py reads the logs back at build
// time. No cookie, no identifier, nothing stored on the device, and the access
// logs don't record IP addresses, user agents or referrers.
//
// Off the production host (zola serve, Lighthouse CI), the beacon is only
// printed to the console.
import {onCLS, onFCP, onINP, onLCP, onTTFB} from './web-vitals-6.2.3.js';

const queue = new Map();

function flush() {
  if (!queue.size) return;
  const metrics = [...queue.values()];
  queue.clear();
  const fields = [
    'p=' + encodeURIComponent(location.pathname),
    'n=' + metrics[0].navigationType,
    // Layout class, not device: the breakpoint where tabi's layout narrows.
    'd=' + (matchMedia('(max-width: 767px)').matches ? 'm' : 'd'),
    ...metrics.map((m) =>
      m.name.toLowerCase() + '=' + (m.name === 'CLS' ? m.value.toFixed(3) : Math.round(m.value))),
  ];
  const url = '/rum/1/' + fields.join(';');
  if (location.hostname === 'idle-ti.me') {
    navigator.sendBeacon(url);
  } else {
    console.debug('[rum]', url);
  }
}

for (const on of [onCLS, onFCP, onINP, onLCP, onTTFB]) {
  on((metric) => queue.set(metric.name, metric));
}
addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') flush();
});
// Safari doesn't always fire visibilitychange when a page is left.
addEventListener('pagehide', flush);
