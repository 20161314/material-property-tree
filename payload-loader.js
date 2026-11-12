(() => {
  const tag = document.currentScript;
  const ready = (async () => {
    const url = new URL(tag.dataset.src, location.href);
    if (url.origin !== location.origin) throw new Error('Payload must be same-origin');
    const response = await fetch(url);
    if (!response.ok) throw new Error('Payload HTTP ' + response.status);
    let bytes = new Uint8Array(await response.arrayBuffer());
    if (bytes[0] === 31 && bytes[1] === 139) {
      if (typeof DecompressionStream !== 'function') throw new Error('浏览器不支持 gzip 数据解压，请使用新版浏览器。');
      bytes = new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
    }
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))).map(x => x.toString(16).padStart(2, '0')).join('');
    if (digest !== tag.dataset.sha256) throw new Error('Payload SHA-256 mismatch');
    const source = new TextDecoder().decode(bytes);
    const position = source.indexOf('=');
    window[tag.dataset.key] = JSON.parse(source.slice(position + 1).trim().replace(/;$/, ''));
  })();
  window.MATERIAL_PAYLOAD_READY = ready;
  ready.catch(error => {
    const box = document.createElement('p'); box.setAttribute('role', 'alert');
    box.style.cssText = 'padding:16px;color:#a00;background:#fff';
    box.textContent = '材料数据载入失败：' + error.message; document.body.appendChild(box);
  });
})();
