const el = id => document.getElementById(id);
const source = el("source"), result = el("result");
const settings = {
  threshold: ["Minimum intensity", 255, 128],
  region: ["Seed tolerance", 255, 18],
  noise: ["Standard deviation", 100, 20],
  smooth: ["Radius (pixels)", 8, 2]
};
let pixels, revision = 0, loading = 0, filename = "";
function draw(canvas, width, height, data) {
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d"), image = ctx.createImageData(width, height);
  for (let i = 0; i < data.length; i++) {
    image.data.fill(data[i], i * 4, i * 4 + 3);
    image.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(image, 0, 0);
}
function invalidate() {
  revision++;
  result.hidden = true;
  el("empty").hidden = false;
  el("export").disabled = true;
  el("run").disabled = false;
  el("resultName").textContent = "Awaiting run";
  el("status").textContent = "Ready to process.";
}
function load(name, width, height, data) {
  pixels = data;
  filename = name;
  draw(source, width, height, data);
  el("filename").textContent = name + " · " + width + " × " + height;
  for (const [id, size] of [["x", width], ["y", height]]) {
    el(id).max = size - 1;
    el(id).value = Math.floor(size / 2);
  }
  invalidate();
}
function sample() {
  loading++;
  const size = 320, data = new Uint8Array(size * size);
  // A mathematical phantom with compartments of known grayscale intensity.
  for (let i = 0; i < data.length; i++) {
    const x = ((i % size) - 160) / 120, y = (Math.floor(i / size) - 160) / 148;
    const r = x*x + y*y;
    let intensity = r < 1 ? (r > 0.91 ? 208 : 98) : 15;
    if (((Math.abs(x)-0.36)/0.19)**2 + ((y+0.1)/0.34)**2 < 1) intensity = 46;
    if ((x/0.18)**2 + ((y-0.53)/0.15)**2 < 1) intensity = 176;
    data[i] = intensity;
  }
  load("Synthetic phantom", size, size, data);
}
function configure() {
  const [label, max, value] = settings[el("operation").value];
  el("param").textContent = label;
  el("amount").max = max;
  el("amount").value = el("value").value = value;
  el("seed").hidden = el("operation").value !== "region";
  for (const id of ["x", "y"]) el(id).disabled = el("seed").hidden;
  invalidate();
}
el("operation").onchange = configure;
el("controls").oninput = () => { el("value").value = el("amount").value; invalidate(); };
el("sample").onclick = sample;
el("import").onclick = () => el("file").click();
el("file").onchange = async event => {
  const file = event.target.files[0];
  event.target.value = "";
  if (!file) return;
  const id = ++loading;
  try {
    if (!["image/png","image/jpeg"].includes(file.type) || file.size > 12*1024*1024)
      throw Error("Choose a PNG or JPEG under 12 MiB.");
    const bitmap = await createImageBitmap(file);
    try {
      if (id !== loading) return;
      const scale = Math.min(1, 1024 / Math.max(bitmap.width, bitmap.height));
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(bitmap.width * scale));
      canvas.height = Math.max(1, Math.round(bitmap.height * scale));
      const ctx = canvas.getContext("2d");
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      const rgba = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      const gray = Uint8Array.from({length: rgba.length/4}, (_, i) =>
        Math.round(.2126*rgba[4*i] + .7152*rgba[4*i+1] + .0722*rgba[4*i+2]));
      load(file.name, canvas.width, canvas.height, gray);
    } finally { bitmap.close(); }
  } catch (error) { if (id === loading) el("status").textContent = "Import failed. " + error.message; }
};
el("controls").onsubmit = async event => {
  event.preventDefault();
  invalidate();
  const id = revision;
  el("run").disabled = true;
  el("status").textContent = "Processing image…";
  const params = new URLSearchParams({operation:el("operation").value, width:source.width, height:source.height,
    amount:el("amount").value, x:el("seed").hidden ? 0 : el("x").value, y:el("seed").hidden ? 0 : el("y").value});
  try {
    const response = await fetch("/api/process?" + params, {method:"POST",headers:{"Content-Type":"application/octet-stream"},body:pixels});
    if (!response.ok) throw Error((await response.json()).error);
    const output = new Uint8Array(await response.arrayBuffer());
    if (id !== revision) return;
    if (output.length !== pixels.length) throw Error("Incomplete image received.");
    draw(result, source.width, source.height, output);
    result.hidden = false;
    el("empty").hidden = true;
    el("export").disabled = false;
    el("resultName").textContent = el("operation").selectedOptions[0].textContent;
    el("status").textContent = "Complete · " + output.length.toLocaleString() + " pixels processed.";
  } catch (error) { if (id === revision) el("status").textContent = "Processing failed. " + error.message; }
  finally { if (id === revision) el("run").disabled = false; }
};
el("export").onclick = () => {
  const link = document.createElement("a");
  link.download = filename.replace(/\.[^.]+$/, "") + "-" + el("operation").value + ".png";
  link.href = result.toDataURL("image/png");
  link.click();
};
configure();
sample();
