(() => {
  const tag = {dataset:{"src": "research-bootstrap.js.gz?v=b5119e94017d", "key": "SITE_DATA", "sha256": "8d6909bae665d6a298280c84295eb940d4bc98eaf4773cfc4bc9ded1868c55de"}};
  const setStatus = (message, failed = false) => {
    let box = document.getElementById('payload-status');
    if (!box) {
      box = document.createElement('p'); box.id = 'payload-status';
      box.style.cssText = 'padding:14px 20px;margin:12px;color:#244052;background:#eaf1f5;border-radius:8px';
      (document.querySelector('main') || document.body).prepend(box);
    }
    box.hidden = false; box.setAttribute('role', failed ? 'alert' : 'status');
    box.replaceChildren(document.createTextNode(message));
    if (failed) {
      const retry = document.createElement('button'); retry.type = 'button'; retry.textContent = '重新载入';
      retry.style.marginLeft = '12px'; retry.addEventListener('click', () => location.reload()); box.appendChild(retry);
    }
  };
  setStatus('正在载入交互数据，请稍候。');
  const ready = (async () => {
    const url = new URL(tag.dataset.src, location.href);
    if (url.origin !== location.origin) throw new Error('Payload must be same-origin');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30000);
    let bytes;
    try {
      const response = await fetch(url, {signal: controller.signal});
      if (!response.ok) throw new Error('HTTP ' + response.status);
      bytes = new Uint8Array(await response.arrayBuffer());
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('网络请求超过30秒，请重试。');
      throw error;
    } finally { clearTimeout(timer); }
    if (bytes[0] === 31 && bytes[1] === 139) {
      if (typeof DecompressionStream !== 'function') throw new Error('浏览器不支持 gzip 解压，请使用新版浏览器。');
      bytes = new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
    }
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))).map(x => x.toString(16).padStart(2, '0')).join('');
    if (digest !== tag.dataset.sha256) throw new Error('数据校验失败，请重试。');
    const source = new TextDecoder().decode(bytes);
    const position = source.indexOf('=');
    window[tag.dataset.key] = JSON.parse(source.slice(position + 1).trim().replace(/;$/, ''));
    document.getElementById('payload-status').hidden = true;
  })();
  window.MATERIAL_PAYLOAD_READY = ready;
  ready.catch(error => setStatus('交互数据载入失败：' + error.message, true));
})();
