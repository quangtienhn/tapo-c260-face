const PANEL_TAG = "tapo-c260-face-manager";

const I18N = {
  "vi": {
    "subtitle": "Quản lý Face ID, tên người và các khuôn mặt chưa nhận diện.",
    "loading": "Đang tải Tapo C260 Face Manager…",
    "noEntries": "Chưa có Tapo C260 nào được cấu hình.",
    "stranger": "Người lạ",
    "strangerId": "Người lạ {id}",
    "cardKnown": "Người quen",
    "cardUnknown": "Người lạ",
    "cardCurrent": "Người hiện tại",
    "cardCurrentId": "Face ID hiện tại",
    "unknownId": "Chưa rõ",
    "addPerson": "＋ Thêm người",
    "refresh": "↻ Làm mới",
    "tabKnown": "Người quen ({n})",
    "tabUnknown": "Người lạ ({n})",
    "tabDay": "Lịch sử ngày",
    "tabStats": "Thống kê",
    "tabSettings": "Cài đặt",
    "relNone": "chưa có",
    "relSec": "{n} giây trước",
    "relMin": "{n} phút trước",
    "relHour": "{n} giờ trước",
    "relDay": "{n} ngày trước",
    "hNotLoaded": "Chưa load",
    "hNotLoadedMsg": "Integration chưa chạy cho camera này (đang lỗi cài đặt hoặc bị tắt) — xem log HA.",
    "hOk": "Kết nối tốt",
    "hWaiting": "Đang chờ Tapo-Control",
    "hStarting": "Đang khởi động",
    "hStale": "Quá hạn — không poll được",
    "hError": "Lỗi truy vấn",
    "mShared": "Dùng chung controller Tapo-Control",
    "mStandalone": "Session riêng",
    "mWait": "Chờ controller Tapo-Control",
    "hLastPoll": "Poll thành công gần nhất",
    "hResponse": "Phản hồi",
    "hMode": "Chế độ",
    "hFailures": "Lỗi liên tiếp",
    "hFailuresTotal": "(tổng {n})",
    "hEvents": "Event xử lý",
    "hDedup": "bỏ do dedup",
    "hBanner": "Camera có thể đang mất kết nối — lúc này \"không thấy ai\" chưa chắc là không có ai.",
    "hLastError": "Lỗi gần nhất ({when}): {err}",
    "dayPrev": "‹ Hôm trước",
    "dayNext": "Hôm sau ›",
    "dayToday": "Hôm nay",
    "loadingShort": "Đang tải…",
    "times": "{n} lần",
    "dayFirstLast": "Đầu tiên {a} · gần nhất {b}",
    "dayNoTimes": "chưa có mốc giờ",
    "dayAppearances": "Các lần xuất hiện ({n})",
    "dayUntimed": "{n} lần ghi trước khi có lịch sử giờ (bản cũ), không có mốc giờ.",
    "dayNobody": "Không có ai xuất hiện ngày {d}.",
    "dayLegend": "Mỗi vạch là một lần xuất hiện (giờ HA). Người quen: xám; người lạ: màu chủ đạo. Người quen bị cooldown dedup nên không tính các lần lặp trong thời gian cooldown.",
    "sPoll": "Polling / Dedup",
    "sPollInterval": "Polling interval (giây)",
    "sPollIntervalHint": "Bao lâu hỏi camera một lần.",
    "sHistory": "History window (giây)",
    "sHistoryHint": "Cửa sổ event lấy mỗi lần poll.",
    "sDedup": "Dedup người quen (giây)",
    "sDedupHint": "Cooldown cho cùng một người quen. 0 = tắt. Người lạ không bị dedup.",
    "sStranger": "Tự tắt \"Stranger Detected\" sau (giây)",
    "sStrangerHint": "Binary sensor người lạ.",
    "sStorage": "Giới hạn lưu trữ",
    "sRetention": "Số ngày giữ thống kê / người lạ",
    "sRetentionHint": "Cũ hơn sẽ bị xoá tự động.",
    "sMaxUnknown": "Số người lạ tối đa",
    "sMaxUnknownHint": "Vượt quá thì bỏ người lâu không thấy nhất.",
    "sDisplay": "Hiển thị",
    "sSidebar": "Hiện Face Manager ở sidebar",
    "sSidebarHint": "Tắt vẫn vào được qua /tapo_c260_face.",
    "sTitle": "Tên ở sidebar",
    "sTitleHint": "Để trống = \"Tapo C260 Face Manager\" (tối đa 40 ký tự). Nhiều camera: dùng tên của camera đầu tiên đang bật sidebar.",
    "sSave": "Lưu cài đặt",
    "sReset": "Hoàn tác",
    "sIntErr": "Các ô số phải là số nguyên.",
    "sSaved": "Đã lưu và áp dụng.",
    "sSidebarShown": " Sidebar: hiện \"{title}\" (nếu chưa đổi, tải lại trang bằng Ctrl+F5).",
    "sSidebarHidden": " Sidebar: đang ẩn.",
    "colFaceId": "Face ID",
    "colName": "Tên",
    "edit": "Sửa",
    "delete": "Xóa",
    "noKnown": "Chưa có người nào. Bấm “Thêm người” để bắt đầu.",
    "uHint": "Giữ tối đa {max} người lạ / {days} ngày (đổi ở Cài đặt → Giới hạn lưu trữ).",
    "uClear": "Xoá tất cả người lạ",
    "uNone": "Chưa phát hiện Face ID lạ.",
    "colFirst": "Lần đầu",
    "colLast": "Lần cuối",
    "colCount": "Số lần",
    "uForget": "Bỏ qua",
    "uMore": "Xem thêm (còn {n})",
    "rangeDays": "{n} ngày",
    "viewChart": "Biểu đồ",
    "viewTable": "Bảng",
    "statsLoading": "Đang tải thống kê…",
    "stToday": "Người lạ hôm nay",
    "st7": "7 ngày",
    "st30": "30 ngày",
    "stTotal": "Tổng lần (toàn bộ record)",
    "stDistinct": "Số Face ID lạ",
    "stPeak": "Ngày cao điểm",
    "colDate": "Ngày",
    "legendUnknown": "Người lạ",
    "legendKnown": "Người quen",
    "ariaDay": "{d}: {u} người lạ, {k} người quen",
    "colDaysSeen": "Số ngày thấy",
    "stNoUnknown": "Chưa có người lạ nào trong lịch sử.",
    "stNoKnown": "Chưa có người quen.",
    "stSince": "Số liệu bắt đầu từ {d}.",
    "stNoData": "Chưa có số liệu.",
    "stDailyTitle": "Số lần xuất hiện theo ngày ({n} ngày gần nhất)",
    "stTopTitle": "Người lạ xuất hiện nhiều nhất",
    "stKnownTitle": "Người quen",
    "stFoot": "{since} Giữ tối đa {days} ngày. Tên được tra theo danh sách hiện tại nên đổi tên sẽ áp dụng cho toàn bộ record.",
    "tipUnknown": "Người lạ: {n}",
    "tipKnown": "Người quen: {n}",
    "save": "Lưu",
    "cancel": "Hủy",
    "errFaceId": "Face ID phải là chuỗi số.",
    "errName": "Tên không được để trống.",
    "cfDelete": "Xóa Face ID {id}? ID này sẽ quay lại danh sách Unknown cùng số lần đã ghi.",
    "cfForget": "Bỏ qua Face ID {id}? Số liệu thống kê của ID này cũng bị xoá. Nó sẽ được ghi nhận lại từ đầu nếu camera phát hiện lần sau.",
    "cfClear": "Xoá toàn bộ {n} người lạ và số liệu thống kê của họ? Không hoàn tác được.",
    "langLabel": "Ngôn ngữ"
  },
  "en": {
    "subtitle": "Manage Face IDs, names and faces that are not identified yet.",
    "loading": "Loading Tapo C260 Face Manager…",
    "noEntries": "No Tapo C260 is configured yet.",
    "stranger": "Stranger",
    "strangerId": "Stranger {id}",
    "cardKnown": "Known faces",
    "cardUnknown": "Unknown faces",
    "cardCurrent": "Current face",
    "cardCurrentId": "Current Face ID",
    "unknownId": "Unknown",
    "addPerson": "＋ Add person",
    "refresh": "↻ Refresh",
    "tabKnown": "Known ({n})",
    "tabUnknown": "Unknown ({n})",
    "tabDay": "Day history",
    "tabStats": "Statistics",
    "tabSettings": "Settings",
    "relNone": "never",
    "relSec": "{n} s ago",
    "relMin": "{n} min ago",
    "relHour": "{n} h ago",
    "relDay": "{n} d ago",
    "hNotLoaded": "Not loaded",
    "hNotLoadedMsg": "The integration is not running for this camera (setup error or disabled) — check the HA log.",
    "hOk": "Connected",
    "hWaiting": "Waiting for Tapo-Control",
    "hStarting": "Starting",
    "hStale": "Stale — cannot poll",
    "hError": "Query error",
    "mShared": "Shared Tapo-Control controller",
    "mStandalone": "Own session",
    "mWait": "Waiting for Tapo-Control controller",
    "hLastPoll": "Last successful poll",
    "hResponse": "Response",
    "hMode": "Mode",
    "hFailures": "Consecutive errors",
    "hFailuresTotal": "(total {n})",
    "hEvents": "Events processed",
    "hDedup": "skipped by dedup",
    "hBanner": "The camera may be disconnected — \"nobody seen\" does not necessarily mean nobody is there.",
    "hLastError": "Last error ({when}): {err}",
    "dayPrev": "‹ Previous day",
    "dayNext": "Next day ›",
    "dayToday": "Today",
    "loadingShort": "Loading…",
    "times": "{n}×",
    "dayFirstLast": "First {a} · latest {b}",
    "dayNoTimes": "no timestamps",
    "dayAppearances": "Appearances ({n})",
    "dayUntimed": "{n} detections were recorded before time history existed (older version), no timestamps.",
    "dayNobody": "Nobody appeared on {d}.",
    "dayLegend": "Each tick is one appearance (HA time). Known people: grey; strangers: accent colour. Repeated sightings of a known person inside the dedup cooldown are not counted.",
    "sPoll": "Polling / Dedup",
    "sPollInterval": "Polling interval (seconds)",
    "sPollIntervalHint": "How often the camera is queried.",
    "sHistory": "History window (seconds)",
    "sHistoryHint": "Event window requested on each poll.",
    "sDedup": "Known-person dedup (seconds)",
    "sDedupHint": "Cooldown for the same known person. 0 = off. Strangers are never deduplicated.",
    "sStranger": "Auto-off \"Stranger Detected\" after (seconds)",
    "sStrangerHint": "Stranger binary sensor.",
    "sStorage": "Storage limits",
    "sRetention": "Days to keep statistics / strangers",
    "sRetentionHint": "Older data is removed automatically.",
    "sMaxUnknown": "Maximum number of strangers",
    "sMaxUnknownHint": "When exceeded, the least recently seen are dropped.",
    "sDisplay": "Display",
    "sSidebar": "Show Face Manager in the sidebar",
    "sSidebarHint": "When off, it is still reachable at /tapo_c260_face.",
    "sTitle": "Sidebar name",
    "sTitleHint": "Leave empty for \"Tapo C260 Face Manager\" (max 40 characters). With several cameras the first one with the sidebar enabled wins.",
    "sSave": "Save settings",
    "sReset": "Revert",
    "sIntErr": "Numeric fields must be whole numbers.",
    "sSaved": "Saved and applied.",
    "sSidebarShown": " Sidebar: shown as \"{title}\" (if it has not changed, reload the page with Ctrl+F5).",
    "sSidebarHidden": " Sidebar: hidden.",
    "colFaceId": "Face ID",
    "colName": "Name",
    "edit": "Edit",
    "delete": "Delete",
    "noKnown": "Nobody yet. Press “Add person” to get started.",
    "uHint": "Keeping at most {max} strangers / {days} days (change under Settings → Storage limits).",
    "uClear": "Clear all strangers",
    "uNone": "No unknown Face ID detected yet.",
    "colFirst": "First seen",
    "colLast": "Last seen",
    "colCount": "Count",
    "uForget": "Ignore",
    "uMore": "Show more ({n} left)",
    "rangeDays": "{n} days",
    "viewChart": "Chart",
    "viewTable": "Table",
    "statsLoading": "Loading statistics…",
    "stToday": "Strangers today",
    "st7": "7 days",
    "st30": "30 days",
    "stTotal": "Total (all records)",
    "stDistinct": "Unknown Face IDs",
    "stPeak": "Peak day",
    "colDate": "Date",
    "legendUnknown": "Strangers",
    "legendKnown": "Known people",
    "ariaDay": "{d}: {u} strangers, {k} known",
    "colDaysSeen": "Days seen",
    "stNoUnknown": "No strangers in the history yet.",
    "stNoKnown": "No known people yet.",
    "stSince": "Data starts on {d}.",
    "stNoData": "No data yet.",
    "stDailyTitle": "Appearances per day (last {n} days)",
    "stTopTitle": "Most frequent strangers",
    "stKnownTitle": "Known people",
    "stFoot": "{since} Keeping at most {days} days. Names are looked up from the current list, so renaming applies to all records.",
    "tipUnknown": "Strangers: {n}",
    "tipKnown": "Known: {n}",
    "save": "Save",
    "cancel": "Cancel",
    "errFaceId": "Face ID must contain digits only.",
    "errName": "Name cannot be empty.",
    "cfDelete": "Delete Face ID {id}? It will return to the Unknown list with the counts already recorded.",
    "cfForget": "Ignore Face ID {id}? Its statistics are deleted as well. It will be recorded from scratch if the camera sees it again.",
    "cfClear": "Delete all {n} strangers and their statistics? This cannot be undone.",
    "langLabel": "Language"
  }
};

const LANG_KEY = "tapo_c260_face_lang";


class TapoC260FaceManager extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._data = null;
    this._entryId = null;
    this._tab = "known";
    this._editing = null;
    this._saving = false;
    this._renderTimer = null;
    this._loading = null;
    this._error = "";
    this._stats = null;
    this._statsDays = 30;
    this._statsView = "chart";
    this._statsSeq = 0;
    this._unknownLimit = 20;
    this._dayData = null;
    this._dayDate = null; // null = hôm nay (theo giờ HA)
    this._daySeq = 0;
    this._draft = null; // bản nháp tab Cài đặt (null = chưa sửa)
    this._settingsMsg = "";
    this._healthTimer = null;
    this._lang = this._initialLang();
    // Gắn listener MỘT LẦN trên shadowRoot (event delegation). shadowRoot không
    // bị thay khi innerHTML đổi, nên không cần bind lại và không bị gắn trùng.
    this.shadowRoot.addEventListener("click", e => this._onClick(e));
    this.shadowRoot.addEventListener("input", e => this._onInput(e));
    this.shadowRoot.addEventListener("change", e => this._onChange(e));
    this.shadowRoot.addEventListener("mouseover", e => this._onOver(e));
    this.shadowRoot.addEventListener("focusin", e => this._onOver(e));
    this.shadowRoot.addEventListener("mouseleave", () => this._hideTip());
    this.shadowRoot.addEventListener("focusout", () => this._hideTip());
  }

  // Ngôn ngữ: lựa chọn đã lưu > ngôn ngữ của HA (vi → Tiếng Việt, còn lại → English).
  _initialLang() {
    try {
      const saved = localStorage.getItem(LANG_KEY);
      if (saved === "vi" || saved === "en") return saved;
    } catch (_) { /* localStorage có thể bị chặn */ }
    return "en";
  }

  _hasSavedLang() {
    try { return ["vi", "en"].includes(localStorage.getItem(LANG_KEY)); } catch (_) { return false; }
  }

  _setLang(lang) {
    if (lang !== "vi" && lang !== "en") return;
    this._lang = lang;
    try { localStorage.setItem(LANG_KEY, lang); } catch (_) { /* bỏ qua */ }
    this._settingsMsg = "";
    this._render();
  }

  _t(key, vars) {
    let text = (I18N[this._lang] && I18N[this._lang][key]) ?? I18N.en[key] ?? key;
    if (vars) for (const [k, v] of Object.entries(vars)) text = text.replaceAll(`{${k}}`, String(v));
    return text;
  }

  _stranger(name) {
    return !name || name === "Stranger" || name === "Người lạ" ? this._t("stranger") : name;
  }

  set hass(hass) {
    const wasReady = !!this._hass;
    this._hass = hass;
    if (!this._hasSavedLang()) {
      const lang = String(hass?.locale?.language || hass?.language || "").toLowerCase();
      this._lang = lang.startsWith("vi") ? "vi" : "en";
    }
    // hass được HA set lại mỗi khi có state đổi: chỉ load lần đầu.
    if (!wasReady) {
      this._render();
      this._load();
    }
  }

  set panel(_panel) {}

  connectedCallback() {
    this._render();
    if (this._hass) {
      this._load();
    }
    // Cập nhật thẻ sức khoẻ định kỳ mà không vẽ lại cả trang.
    clearInterval(this._healthTimer);
    this._healthTimer = setInterval(() => this._pollHealth(), 15000);
  }

  disconnectedCallback() {
    clearInterval(this._healthTimer);
    this._healthTimer = null;
  }

  async _pollHealth() {
    if (!this._hass || this._saving) return;
    try {
      const result = await this._ws({ type: "tapo_c260_face/get_data" });
      const fresh = result.entries?.find(e => e.entry_id === this._entryId);
      if (!fresh || !this._data) return;
      const i = this._data.entries.findIndex(e => e.entry_id === this._entryId);
      if (i >= 0) this._data.entries[i] = { ...this._data.entries[i], health: fresh.health };
      const box = this.shadowRoot.querySelector("#health");
      if (box) box.innerHTML = this._renderHealth(fresh);
    } catch (_) { /* lần sau thử lại */ }
  }

  async _ws(message) {
    if (!this._hass) throw new Error("Home Assistant is not ready");
    return this._hass.connection.sendMessagePromise(message);
  }

  // Dedupe: nhiều nơi gọi cùng lúc (hass setter, connectedCallback) chỉ chạy 1 request.
  // force=true: dùng sau save/delete, đợi request đang bay xong rồi load lại để
  // không nhận data cũ (trước khi lưu).
  _load(force = false) {
    if (!this._hass) return Promise.resolve();
    if (this._loading && !force) return this._loading;

    const run = async () => {
      try {
        const result = await this._ws({ type: "tapo_c260_face/get_data" });
        this._data = result;
        if (!this._entryId && result.entries?.length) {
          this._entryId = result.entries[0].entry_id;
        }
        if (this._entryId && !result.entries?.some(e => e.entry_id === this._entryId)) {
          this._entryId = result.entries?.[0]?.entry_id || null;
        }
        this._error = "";
      } catch (err) {
        this._error = err?.message || String(err);
      }
      // Đang mở form thì chỉ cập nhật data ngầm, không vẽ lại.
      if (!this._editing && !(this._draft && this._tab === "settings")) this._render();
      if (this._tab === "stats") this._fetchStats();
      if (this._tab === "day") this._fetchDay();
    };

    const prev = this._loading;
    const p = (prev ? prev.then(run) : run()).finally(() => {
      if (this._loading === p) this._loading = null;
    });
    this._loading = p;
    return p;
  }

  // Thống kê: tính ở backend (tên người tra theo danh sách hiện tại).
  async _fetchStats() {
    if (!this._hass || !this._entryId) return;
    const seq = ++this._statsSeq;
    try {
      const result = await this._ws({
        type: "tapo_c260_face/get_stats",
        entry_id: this._entryId,
        range_days: this._statsDays
      });
      if (seq !== this._statsSeq) return;
      this._stats = result.stats;
      this._error = "";
    } catch (err) {
      if (seq !== this._statsSeq) return;
      this._error = err?.message || String(err);
    }
    if (!this._editing && this._tab === "stats") this._render();
  }

  // Lịch sử trong ngày: ai xuất hiện lúc nào (giờ theo múi giờ HA).
  async _fetchDay() {
    if (!this._hass || !this._entryId) return;
    const seq = ++this._daySeq;
    try {
      const msg = { type: "tapo_c260_face/get_day", entry_id: this._entryId };
      if (this._dayDate) msg.date = this._dayDate;
      const result = await this._ws(msg);
      if (seq !== this._daySeq) return;
      this._dayData = result.day;
      this._error = "";
    } catch (err) {
      if (seq !== this._daySeq) return;
      this._error = err?.message || String(err);
    }
    if (!this._editing && this._tab === "day") this._render();
  }

  _entry() {
    return this._data?.entries?.find(e => e.entry_id === this._entryId) || null;
  }

  _esc(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  _render(focusId = null) {
    if (!this.shadowRoot) return;
    // Nhớ ô đang focus + vị trí con trỏ để khôi phục sau khi vẽ lại.
    const active = this.shadowRoot.activeElement;
    const keep = active && (active.id === "face-id" || active.id === "face-name")
      ? { id: active.id, start: active.selectionStart, end: active.selectionEnd }
      : null;
    const entry = this._entry();
    const entries = this._data?.entries || [];

    if (!this._data && !this._error) {
      this.shadowRoot.innerHTML = `
        <style>
          :host { display:block; color:var(--primary-text-color); background:var(--primary-background-color); min-height:100%; }
          .loading { padding:40px; font-size:18px; color:var(--secondary-text-color); }
        </style>
        <div class="loading">${this._t("loading")}</div>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host { display:block; color:var(--primary-text-color); background:var(--primary-background-color); min-height:100%; }
        .wrap { max-width:1180px; margin:0 auto; padding:24px; box-sizing:border-box; }
        h1 { font-size:28px; margin:0 0 4px; font-weight:500; }
        .sub { color:var(--secondary-text-color); margin-bottom:20px; }
        .head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap; }
        .toolbar { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:18px; }
        select,input,button { font:inherit; }
        select,input { background:var(--card-background-color); color:var(--primary-text-color); border:1px solid var(--divider-color); border-radius:8px; padding:10px 12px; box-sizing:border-box; }
        select { min-width:280px; }
        button { border:0; border-radius:8px; padding:10px 14px; cursor:pointer; color:var(--text-primary-color); background:var(--primary-color); }
        button.secondary { background:var(--secondary-background-color); color:var(--primary-text-color); }
        button.danger { background:var(--error-color); color:white; }
        button:disabled { opacity:.5; cursor:not-allowed; }
        .cards { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:20px; }
        .stat { background:var(--ha-card-background,var(--card-background-color)); border-radius:12px; padding:16px; box-shadow:var(--ha-card-box-shadow); }
        .stat .label { color:var(--secondary-text-color); font-size:13px; }
        .stat .value { font-size:24px; margin-top:6px; }
        .current { grid-column:span 1; }
        .panel { background:var(--ha-card-background,var(--card-background-color)); border-radius:12px; box-shadow:var(--ha-card-box-shadow); overflow:hidden; }
        .tabs { display:flex; border-bottom:1px solid var(--divider-color); }
        .tab { background:transparent; color:var(--secondary-text-color); border-radius:0; border-bottom:3px solid transparent; }
        .tab.active { color:var(--primary-color); border-bottom-color:var(--primary-color); }
        table { width:100%; border-collapse:collapse; }
        th,td { text-align:left; padding:13px 16px; border-bottom:1px solid var(--divider-color); vertical-align:middle; }
        th { color:var(--secondary-text-color); font-size:13px; font-weight:500; }
        .id { font-family:monospace; font-size:14px; }
        .actions { display:flex; gap:7px; flex-wrap:wrap; justify-content:flex-end; }
        .actions button { padding:7px 10px; font-size:13px; }
        .empty { padding:32px; text-align:center; color:var(--secondary-text-color); }
        .form { padding:18px; border-bottom:1px solid var(--divider-color); display:grid; grid-template-columns:1fr 1fr auto; gap:10px; align-items:end; }
        .field label { display:block; color:var(--secondary-text-color); font-size:12px; margin:0 0 5px; }
        .error { color:var(--error-color); padding:12px 0; }
        .badge { display:inline-block; padding:3px 8px; border-radius:999px; font-size:12px; background:var(--secondary-background-color); }
        .known { color:var(--success-color); }
        .hint { color:var(--secondary-text-color); font-size:13px; padding:12px 16px; border-bottom:1px solid var(--divider-color); display:flex; gap:10px; align-items:center; justify-content:space-between; flex-wrap:wrap; }
        .more { padding:14px; text-align:center; }
        .stats { padding:16px; }
        .stats h3 { font-size:15px; font-weight:500; margin:22px 0 10px; }
        .stats h3:first-child { margin-top:0; }
        .mini { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:10px; margin-bottom:6px; }
        .mini .stat { padding:12px; box-shadow:none; border:1px solid var(--divider-color); }
        .mini .value { font-size:20px; }
        .seg { display:inline-flex; border:1px solid var(--divider-color); border-radius:8px; overflow:hidden; }
        .seg button { border-radius:0; background:transparent; color:var(--secondary-text-color); padding:7px 12px; }
        .seg button.on { background:var(--primary-color); color:var(--text-primary-color); }
        .chart-head { display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:10px; }
        .legend { display:flex; gap:16px; font-size:13px; color:var(--secondary-text-color); }
        .legend i { display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; vertical-align:-1px; }
        .sw-unknown { background:var(--primary-color); }
        .sw-known { background:var(--disabled-text-color, #9e9e9e); }
        .chart { position:relative; height:170px; display:flex; align-items:flex-end; justify-content:center; gap:3px; padding:0 0 0 34px; border-bottom:1px solid var(--divider-color); }
        .chart .ymax { position:absolute; left:0; top:-2px; font-size:11px; color:var(--secondary-text-color); }
        .chart .grid { position:absolute; left:34px; right:0; top:0; border-top:1px dashed var(--divider-color); }
        .col { flex:1 1 0; max-width:24px; min-width:3px; height:100%; display:flex; flex-direction:column; justify-content:flex-end; gap:2px; outline:none; position:relative; }
        .col:hover, .col:focus { background:var(--secondary-background-color); }
        .col .u, .col .k { width:100%; }
        .col .u { background:var(--primary-color); }
        .col .k { background:var(--disabled-text-color, #9e9e9e); }
        .col .top { border-radius:4px 4px 0 0; }
        .xaxis { display:flex; justify-content:space-between; font-size:11px; color:var(--secondary-text-color); padding:4px 0 0 34px; }
        .tip { position:absolute; z-index:2; pointer-events:none; background:var(--card-background-color); color:var(--primary-text-color); border:1px solid var(--divider-color); border-radius:8px; padding:8px 10px; font-size:12px; box-shadow:var(--ha-card-box-shadow, 0 2px 8px rgba(0,0,0,.25)); white-space:nowrap; display:none; }
        .scroll { max-height:340px; overflow:auto; }
        .health { background:var(--ha-card-background,var(--card-background-color)); border-radius:12px; box-shadow:var(--ha-card-box-shadow); padding:14px 16px; margin-bottom:16px; }
        .health .row { display:flex; flex-wrap:wrap; gap:8px 22px; align-items:center; }
        .health .kv { font-size:13px; color:var(--secondary-text-color); }
        .health .kv b { color:var(--primary-text-color); font-weight:500; }
        .chip { display:inline-flex; align-items:center; gap:6px; padding:3px 10px; border-radius:999px; font-size:13px; background:var(--secondary-background-color); color:var(--primary-text-color); }
        .chip::before { content:""; width:8px; height:8px; border-radius:50%; background:var(--disabled-text-color,#9e9e9e); }
        .chip.ok::before { background:var(--success-color,#43a047); }
        .chip.warn::before { background:var(--warning-color,#ffa000); }
        .chip.bad::before { background:var(--error-color,#db4437); }
        .banner { margin-top:10px; padding:10px 12px; border-radius:8px; font-size:13px; border:1px solid var(--error-color,#db4437); color:var(--primary-text-color); }
        .daynav { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:14px; }
        .person { padding:12px 0; border-bottom:1px solid var(--divider-color); }
        .person:last-child { border-bottom:0; }
        .person .top { display:flex; gap:10px; align-items:baseline; flex-wrap:wrap; }
        .person .nm { font-weight:500; }
        .person .meta { color:var(--secondary-text-color); font-size:13px; }
        .strip { position:relative; height:14px; margin:8px 0 2px; background:var(--secondary-background-color); border-radius:4px; }
        .strip .tick { position:absolute; top:0; bottom:0; width:2px; margin-left:-1px; background:var(--disabled-text-color,#9e9e9e); }
        .strip .tick.u { background:var(--primary-color); }
        .hours { position:relative; height:14px; font-size:11px; color:var(--secondary-text-color); }
        .hours span { position:absolute; transform:translateX(-50%); }
        .hours span:first-child { transform:none; } .hours span:last-child { transform:translateX(-100%); }
        details.times { margin-top:4px; font-size:13px; color:var(--secondary-text-color); }
        details.times summary { cursor:pointer; }
        .settings { padding:16px; max-width:640px; }
        .settings fieldset { border:1px solid var(--divider-color); border-radius:10px; margin:0 0 14px; padding:10px 14px 14px; }
        .settings legend { color:var(--secondary-text-color); font-size:13px; padding:0 6px; }
        .srow { display:grid; grid-template-columns:1fr 130px; gap:10px; align-items:center; padding:7px 0; }
        .srow small { display:block; color:var(--secondary-text-color); }
        .srow input[type=number], .srow input[type=text] { width:100%; }
        .ok-msg { color:var(--success-color,#43a047); margin-left:8px; }
        @media(max-width:800px) { .mini{grid-template-columns:repeat(2,1fr);} .wrap{padding:14px;} .cards{grid-template-columns:repeat(2,1fr);} .form{grid-template-columns:1fr;} table,thead,tbody,tr,th,td{display:block;} thead{display:none;} tr{padding:10px 14px;border-bottom:1px solid var(--divider-color);} td{border:0;padding:5px 0;} .actions{justify-content:flex-start;} }
      </style>
      <div class="wrap">
        <div class="head">
          <div>
            <h1>Tapo C260 Face Manager</h1>
            <div class="sub">${this._t("subtitle")}</div>
          </div>
          <div class="seg" role="group" aria-label="${this._t("langLabel")}">
            <button class="lang ${this._lang === "vi" ? "on" : ""}" data-lang="vi" aria-pressed="${this._lang === "vi"}">VI</button>
            <button class="lang ${this._lang === "en" ? "on" : ""}" data-lang="en" aria-pressed="${this._lang === "en"}">EN</button>
          </div>
        </div>
        ${entries.length > 1 ? `
          <div class="toolbar">
            <select id="camera">
              ${entries.map(e => `<option value="${this._esc(e.entry_id)}" ${e.entry_id === this._entryId ? "selected" : ""}>${this._esc(e.title)} — ${this._esc(e.host)}</option>`).join("")}
            </select>
          </div>` : ""}
        ${this._error ? `<div class="error">${this._esc(this._error)}</div>` : ""}
        ${entry ? this._renderEntry(entry) : `<div class="empty">${this._t("noEntries")}</div>`}
      </div>
    `;
    this._restoreFocus(focusId, keep);
  }

  _restoreFocus(focusId, keep) {
    if (!this._editing) return;
    const id = focusId || keep?.id;
    if (!id) return;
    const el = this.shadowRoot.querySelector(`#${id}`);
    if (!el) return;
    el.focus();
    if (!focusId && keep && keep.start != null) {
      try { el.setSelectionRange(keep.start, keep.end); } catch (_) { /* ignore */ }
    }
  }

  _renderEntry(entry) {
    const current = entry.current || {};
    const known = entry.faces || [];
    const unknown = entry.unknown_faces || [];
    return `
      <div class="health" id="health">${this._renderHealth(entry)}</div>
      <div class="cards">
        <div class="stat"><div class="label">${this._t("cardKnown")}</div><div class="value">${known.length}</div></div>
        <div class="stat"><div class="label">${this._t("cardUnknown")}</div><div class="value">${unknown.length}</div></div>
        <div class="stat"><div class="label">${this._t("cardCurrent")}</div><div class="value" style="font-size:18px">${this._esc(this._stranger(current.name))}</div></div>
        <div class="stat"><div class="label">${this._t("cardCurrentId")}</div><div class="value id" style="font-size:16px">${this._esc(current.face_id || this._t("unknownId"))}</div></div>
      </div>
      <div class="toolbar">
        <button id="add">${this._t("addPerson")}</button>
        <button id="refresh" class="secondary">${this._t("refresh")}</button>
      </div>
      <div class="panel">
        <div class="tabs">
          <button class="tab ${this._tab === "known" ? "active" : ""}" data-tab="known">${this._t("tabKnown", { n: known.length })}</button>
          <button class="tab ${this._tab === "unknown" ? "active" : ""}" data-tab="unknown">${this._t("tabUnknown", { n: unknown.length })}</button>
          <button class="tab ${this._tab === "day" ? "active" : ""}" data-tab="day">${this._t("tabDay")}</button>
          <button class="tab ${this._tab === "stats" ? "active" : ""}" data-tab="stats">${this._t("tabStats")}</button>
          <button class="tab ${this._tab === "settings" ? "active" : ""}" data-tab="settings">${this._t("tabSettings")}</button>
        </div>
        ${this._tab === "known" ? this._renderKnown(known)
          : this._tab === "unknown" ? this._renderUnknown(unknown, entry)
          : this._tab === "day" ? this._renderDay()
          : this._tab === "settings" ? this._renderSettings(entry)
          : this._renderStats(entry)}
      </div>
    `;
  }

  _rel(iso) {
    if (!iso) return this._t("relNone");
    const sec = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000));
    if (Number.isNaN(sec)) return "—";
    if (sec < 60) return this._t("relSec", { n: sec });
    if (sec < 3600) return this._t("relMin", { n: Math.round(sec / 60) });
    if (sec < 86400) return this._t("relHour", { n: Math.round(sec / 3600) });
    return this._t("relDay", { n: Math.round(sec / 86400) });
  }

  _renderHealth(entry) {
    const h = entry?.health;
    if (!h) {
      return `<div class="row"><span class="chip warn">${this._t("hNotLoaded")}</span><span class="kv">${this._t("hNotLoadedMsg")}</span></div>`;
    }
    const status = {
      ok: ["ok", this._t("hOk")], waiting: ["warn", this._t("hWaiting")],
      starting: ["warn", this._t("hStarting")], stale: ["bad", this._t("hStale")],
      error: ["bad", this._t("hError")],
    }[h.status] || ["warn", h.status];
    const mode = {
      shared: this._t("mShared"), standalone: this._t("mStandalone"),
      wait: this._t("mWait"), starting: "—",
    }[h.mode] || h.mode;
    const bad = h.status === "error" || h.status === "stale";
    return `
      <div class="row">
        <span class="chip ${status[0]}">${this._esc(status[1])}</span>
        <span class="kv">${this._t("hLastPoll")}: <b>${this._esc(this._rel(h.last_success))}</b></span>
        <span class="kv">${this._t("hResponse")}: <b>${h.response_ms == null ? "—" : h.response_ms + " ms"}</b></span>
        <span class="kv">${this._t("hMode")}: <b>${this._esc(mode)}</b></span>
        <span class="kv">${this._t("hFailures")}: <b>${h.consecutive_failures}</b> ${this._t("hFailuresTotal", { n: h.total_failures })}</span>
        <span class="kv">${this._t("hEvents")}: <b>${h.events_processed}</b> · ${this._t("hDedup")}: <b>${h.dedup_skipped}</b></span>
      </div>
      ${bad ? `<div class="banner">${this._t("hBanner")}${h.last_error ? " " + this._esc(this._t("hLastError", { when: this._rel(h.last_error_time), err: h.last_error })) : ""}</div>` : ""}`;
  }

  _secs(label) {
    const m = /^(\d{2}):(\d{2}):(\d{2})$/.exec(label || "");
    return m ? (+m[1]) * 3600 + (+m[2]) * 60 + (+m[3]) : 0;
  }

  _shiftDay(delta) {
    const base = this._dayData?.date || this._dayDate;
    if (!base) return;
    const [y, m, d] = base.split("-").map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d + delta));
    this._dayDate = dt.toISOString().slice(0, 10);
  }

  _renderDay() {
    const d = this._dayData;
    const nav = `
      <div class="daynav">
        <button class="secondary" data-daynav="-1">${this._t("dayPrev")}</button>
        <input type="date" id="day-date" value="${this._esc(d?.date || this._dayDate || "")}">
        <button class="secondary" data-daynav="1">${this._t("dayNext")}</button>
        <button class="secondary" data-daynav="today">${this._t("dayToday")}</button>
      </div>`;
    if (!d) return `<div class="stats">${nav}<div class="empty">${this._t("loadingShort")}</div></div>`;
    const ticks = (p) => p.times.map(t =>
      `<div class="tick ${p.known ? "" : "u"}" style="left:${(this._secs(t) / 864).toFixed(3)}%" title="${t}"></div>`).join("");
    const hours = `<div class="hours">${[0, 6, 12, 18, 24].map(h => `<span style="left:${h / 24 * 100}%">${h}h</span>`).join("")}</div>`;
    const rows = d.people.map(p => `
      <div class="person">
        <div class="top">
          <span class="nm">${p.known ? this._esc(p.name) : this._esc(this._t("strangerId", { id: p.face_ids[0] }))}</span>
          <span class="badge">${this._t("times", { n: p.count })}</span>
          <span class="meta">${p.first ? this._esc(this._t("dayFirstLast", { a: p.first.slice(0, 5), b: p.last.slice(0, 5) })) : this._t("dayNoTimes")}${p.known && p.face_ids.length > 1 ? ` · ID ${this._esc(p.face_ids.join(", "))}` : ""}</span>
        </div>
        ${p.times.length ? `<div class="strip">${ticks(p)}</div>${hours}
          <details class="times"><summary>${this._t("dayAppearances", { n: p.times.length })}</summary>${this._esc(p.times.join("  ·  "))}</details>` : ""}
        ${p.untimed ? `<div class="meta">${this._t("dayUntimed", { n: p.untimed })}</div>` : ""}
      </div>`).join("");
    return `<div class="stats">${nav}${d.people.length ? rows : `<div class="empty">${this._esc(this._t("dayNobody", { d: this._day(d.date) }))}</div>`}
      <div class="sub" style="margin:12px 0 0">${this._t("dayLegend")}</div></div>`;
  }

  _settingsOf(entry) {
    return {
      poll_interval: entry.poll_interval, history_seconds: entry.history_seconds,
      dedup_seconds: entry.dedup_seconds, stranger_clear_seconds: entry.stranger_clear_seconds,
      retention_days: entry.retention_days, max_unknown_faces: entry.max_unknown_faces,
      show_sidebar: !!entry.show_sidebar, sidebar_title: entry.sidebar_title || "",
    };
  }

  _renderSettings(entry) {
    const v = this._draft || this._settingsOf(entry);
    const num = (key, label, hint, min, max) => `
      <div class="srow"><label for="set-${key}">${label}<small>${hint}</small></label>
        <input type="number" id="set-${key}" data-set="${key}" min="${min}" max="${max}" step="1" value="${this._esc(v[key])}"></div>`;
    return `<div class="settings">
      <fieldset><legend>${this._t("sPoll")}</legend>
        ${num("poll_interval", this._t("sPollInterval"), this._t("sPollIntervalHint"), 2, 300)}
        ${num("history_seconds", this._t("sHistory"), this._t("sHistoryHint"), 30, 3600)}
        ${num("dedup_seconds", this._t("sDedup"), this._t("sDedupHint"), 0, 3600)}
        ${num("stranger_clear_seconds", this._t("sStranger"), this._t("sStrangerHint"), 5, 600)}
      </fieldset>
      <fieldset><legend>${this._t("sStorage")}</legend>
        ${num("retention_days", this._t("sRetention"), this._t("sRetentionHint"), 1, 365)}
        ${num("max_unknown_faces", this._t("sMaxUnknown"), this._t("sMaxUnknownHint"), 10, 1000)}
      </fieldset>
      <fieldset><legend>${this._t("sDisplay")}</legend>
        <div class="srow"><label for="set-show_sidebar">${this._t("sSidebar")}<small>${this._t("sSidebarHint")}</small></label>
          <input type="checkbox" id="set-show_sidebar" data-set="show_sidebar" ${v.show_sidebar ? "checked" : ""}></div>
        <div class="srow"><label for="set-sidebar_title">${this._t("sTitle")}<small>${this._t("sTitleHint")}</small></label>
          <input type="text" id="set-sidebar_title" data-set="sidebar_title" maxlength="40" placeholder="Tapo C260 Face Manager" value="${this._esc(v.sidebar_title)}"></div>
      </fieldset>
      <div class="actions" style="justify-content:flex-start">
        <button id="save-settings" ${this._saving ? "disabled" : ""}>${this._t("sSave")}</button>
        <button id="reset-settings" class="secondary">${this._t("sReset")}</button>
        <span class="ok-msg">${this._esc(this._settingsMsg)}</span>
      </div>
    </div>`;
  }

  async _saveSettings() {
    if (this._saving) return;
    const entry = this._entry();
    if (!entry) return;
    const v = this._draft || this._settingsOf(entry);
    const msg = { type: "tapo_c260_face/save_settings", entry_id: this._entryId };
    for (const key of ["poll_interval", "history_seconds", "dedup_seconds", "stranger_clear_seconds", "retention_days", "max_unknown_faces"]) {
      const n = v[key] === "" || v[key] == null ? NaN : Number(v[key]);
      if (!Number.isInteger(n)) { this._error = this._t("sIntErr"); this._render(); return; }
      msg[key] = n;
    }
    msg.show_sidebar = !!v.show_sidebar;
    msg.sidebar_title = String(v.sidebar_title || "").trim();
    this._saving = true;
    try {
      const result = await this._ws(msg);
      const i = this._data.entries.findIndex(e => e.entry_id === this._entryId);
      if (i >= 0 && result.entry) this._data.entries[i] = result.entry;
      this._draft = null;
      this._error = "";
      this._settingsMsg = this._t("sSaved") + (result.panel ? (result.panel.in_sidebar ? this._t("sSidebarShown", { title: result.panel.title }) : this._t("sSidebarHidden")) : "");
    } catch (err) {
      this._error = err?.message || String(err);
      this._settingsMsg = "";
    }
    this._saving = false;
    this._render();
  }

  _renderKnown(faces) {
    const editing = this._editing;
    return `
      ${editing ? this._renderForm(editing) : ""}
      ${faces.length ? `
        <table><thead><tr><th>${this._t("colFaceId")}</th><th>${this._t("colName")}</th><th></th></tr></thead><tbody>
          ${faces.map(face => `
            <tr>
              <td class="id">${this._esc(face.face_id)}</td>
              <td>${this._esc(face.name)}</td>
              <td><div class="actions">
                <button class="secondary edit" data-id="${this._esc(face.face_id)}">${this._t("edit")}</button>
                <button class="danger delete" data-id="${this._esc(face.face_id)}">${this._t("delete")}</button>
              </div></td>
            </tr>`).join("")}
        </tbody></table>` : `<div class="empty">${this._t("noKnown")}</div>`}
    `;
  }

  _renderUnknown(faces, entry) {
    const shown = faces.slice(0, this._unknownLimit);
    const rest = faces.length - shown.length;
    const hint = `
      <div class="hint">
        <span>${this._t("uHint", { max: entry?.max_unknown_faces ?? "?", days: entry?.retention_days ?? "?" })}</span>
        ${faces.length ? `<button id="clear-unknown" class="danger">${this._t("uClear")}</button>` : ""}
      </div>`;
    if (!faces.length) return `${hint}<div class="empty">${this._t("uNone")}</div>`;
    return `${hint}
      <table><thead><tr><th>${this._t("colFaceId")}</th><th>${this._t("colFirst")}</th><th>${this._t("colLast")}</th><th>${this._t("colCount")}</th><th></th></tr></thead><tbody>
        ${shown.map(face => `
          <tr>
            <td class="id">${this._esc(face.face_id)}</td>
            <td>${this._fmt(face.first_seen)}</td>
            <td>${this._fmt(face.last_seen)}</td>
            <td><span class="badge">${face.count || 0}</span></td>
            <td><div class="actions">
              <button class="add-unknown" data-id="${this._esc(face.face_id)}">${this._t("addPerson")}</button>
              <button class="danger forget" data-id="${this._esc(face.face_id)}">${this._t("uForget")}</button>
            </div></td>
          </tr>`).join("")}
      </tbody></table>
      ${rest > 0 ? `<div class="more"><button id="more-unknown" class="secondary">${this._t("uMore", { n: rest })}</button></div>` : ""}`;
  }

  _renderStats(entry) {
    const st = this._stats;
    const range = [7, 30, 90].map(n =>
      `<button class="range ${this._statsDays === n ? "on" : ""}" data-days="${n}">${this._t("rangeDays", { n })}</button>`).join("");
    const head = `
      <div class="chart-head">
        <div class="seg">${range}</div>
        <div class="seg">
          <button class="view ${this._statsView === "chart" ? "on" : ""}" data-view="chart">${this._t("viewChart")}</button>
          <button class="view ${this._statsView === "table" ? "on" : ""}" data-view="table">${this._t("viewTable")}</button>
        </div>
      </div>`;
    if (!st) return `<div class="stats">${head}<div class="empty">${this._t("statsLoading")}</div></div>`;

    const u = st.unknown || {};
    const peak = u.peak_day ? `${this._day(u.peak_day.date)} (${u.peak_day.count})` : "—";
    const cards = `
      <div class="mini">
        <div class="stat"><div class="label">${this._t("stToday")}</div><div class="value">${u.today ?? 0}</div></div>
        <div class="stat"><div class="label">${this._t("st7")}</div><div class="value">${u.last_7_days ?? 0}</div></div>
        <div class="stat"><div class="label">${this._t("st30")}</div><div class="value">${u.last_30_days ?? 0}</div></div>
        <div class="stat"><div class="label">${this._t("stTotal")}</div><div class="value">${u.total_events ?? 0}</div></div>
        <div class="stat"><div class="label">${this._t("stDistinct")}</div><div class="value">${u.distinct_ids ?? 0}</div></div>
        <div class="stat"><div class="label">${this._t("stPeak")}</div><div class="value" style="font-size:15px">${this._esc(peak)}</div></div>
      </div>`;

    const daily = st.daily || [];
    let body;
    if (this._statsView === "table") {
      const rows = daily.slice().reverse().map(d => `
        <tr><td>${this._esc(this._day(d.date))}</td><td>${d.unknown}</td><td>${d.known}</td></tr>`).join("");
      body = `<div class="scroll"><table><thead><tr><th>${this._t("colDate")}</th><th>${this._t("legendUnknown")}</th><th>${this._t("legendKnown")}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
    } else {
      const max = Math.max(1, ...daily.map(d => d.unknown + d.known));
      const H = 160;
      const cols = daily.map((d, i) => {
        const hu = d.unknown ? Math.max(2, Math.round(d.unknown / max * H)) : 0;
        const hk = d.known ? Math.max(2, Math.round(d.known / max * H)) : 0;
        const topIsU = hu > 0;
        return `<div class="col" tabindex="0" data-i="${i}" role="img" aria-label="${this._esc(this._t("ariaDay", { d: this._day(d.date), u: d.unknown, k: d.known }))}">
          ${hu ? `<div class="u ${topIsU ? "top" : ""}" style="height:${hu}px"></div>` : ""}
          ${hk ? `<div class="k ${!hu ? "top" : ""}" style="height:${hk}px"></div>` : ""}
        </div>`;
      }).join("");
      body = `
        <div class="legend"><span><i class="sw-unknown"></i>${this._t("legendUnknown")}</span><span><i class="sw-known"></i>${this._t("legendKnown")}</span></div>
        <div style="position:relative;margin-top:10px">
          <div class="chart"><span class="ymax">${max}</span><div class="grid"></div>${cols}</div>
          <div class="xaxis"><span>${this._esc(this._day(daily[0]?.date))}</span><span>${this._esc(this._day(daily[daily.length - 1]?.date))}</span></div>
          <div class="tip" id="tip"></div>
        </div>`;
    }

    const top = (u.top || []);
    const topTable = top.length ? `
      <table><thead><tr><th>${this._t("colFaceId")}</th><th>${this._t("colCount")}</th><th>${this._t("colDaysSeen")}</th><th>${this._t("colFirst")}</th><th>${this._t("colLast")}</th><th></th></tr></thead><tbody>
        ${top.map(t => `<tr>
          <td class="id">${this._esc(t.face_id)}</td>
          <td><span class="badge">${t.count}</span></td>
          <td>${t.days_seen}</td>
          <td>${this._esc(this._day(t.first_day))}</td>
          <td>${this._fmt(t.last_seen)}</td>
          <td><div class="actions"><button class="add-unknown" data-id="${this._esc(t.face_id)}">${this._t("addPerson")}</button></div></td>
        </tr>`).join("")}
      </tbody></table>` : `<div class="empty">${this._t("stNoUnknown")}</div>`;

    const persons = (st.known?.persons || []);
    const personTable = persons.length ? `
      <table><thead><tr><th>${this._t("colName")}</th><th>${this._t("colFaceId")}</th><th>${this._t("colCount")}</th><th>${this._t("colLast")}</th></tr></thead><tbody>
        ${persons.map(p => `<tr>
          <td>${this._esc(p.name)}</td>
          <td class="id">${this._esc((p.face_ids || []).join(", "))}</td>
          <td><span class="badge">${p.count}</span></td>
          <td>${this._fmt(p.last_seen)}</td>
        </tr>`).join("")}
      </tbody></table>` : `<div class="empty">${this._t("stNoKnown")}</div>`;

    const since = st.first_day ? this._t("stSince", { d: this._day(st.first_day) }) : this._t("stNoData");
    return `<div class="stats">
      ${head}
      ${cards}
      <h3>${this._t("stDailyTitle", { n: st.range_days })}</h3>
      ${body}
      <h3>${this._t("stTopTitle")}</h3>
      ${topTable}
      <h3>${this._t("stKnownTitle")}</h3>
      ${personTable}
      <div class="sub" style="margin:14px 0 0">${this._esc(this._t("stFoot", { since, days: entry?.retention_days ?? "?" }))}</div>
    </div>`;
  }

  _day(iso) {
    if (!iso) return "—";
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
    return m ? `${m[3]}/${m[2]}/${m[1]}` : String(iso);
  }

  _onOver(e) {
    const col = e.target?.closest?.(".col");
    const tip = this.shadowRoot.querySelector("#tip");
    if (!col || !tip || !this._stats) return;
    const d = this._stats.daily?.[Number(col.dataset.i)];
    if (!d) return;
    tip.innerHTML = `<b>${this._esc(this._day(d.date))}</b><br>${this._esc(this._t("tipUnknown", { n: d.unknown }))}<br>${this._esc(this._t("tipKnown", { n: d.known }))}`;
    tip.style.display = "block";
    const host = tip.parentElement;
    const left = col.getBoundingClientRect().left - host.getBoundingClientRect().left;
    const flip = left > host.clientWidth - 140;
    tip.style.left = flip ? "auto" : `${left + 12}px`;
    tip.style.right = flip ? `${host.clientWidth - left}px` : "auto";
    tip.style.top = "0px";
  }

  _hideTip() {
    const tip = this.shadowRoot.querySelector("#tip");
    if (tip) tip.style.display = "none";
  }

  _renderForm(editing) {
    return `
      <div class="form">
        <div class="field">
          <label>Face ID</label>
          <input id="face-id" type="text" value="${this._esc(editing.face_id || "")}" inputmode="numeric" autocomplete="off" spellcheck="false">
        </div>
        <div class="field">
          <label>${this._t("colName")}</label>
          <input id="face-name" type="text" value="${this._esc(editing.name || "")}" autocomplete="off" spellcheck="false">
        </div>
        <div class="actions">
          <button id="save" type="button">${this._t("save")}</button>
          <button id="cancel" type="button" class="secondary">${this._t("cancel")}</button>
        </div>
      </div>
    `;
  }

  _fmt(value) {
    if (!value) return "—";
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? this._esc(value) : d.toLocaleString(this._lang === "vi" ? "vi-VN" : "en-GB");
  }

  _onClick(e) {
    const btn = e.target?.closest?.("button");
    if (!btn || btn.disabled) return;

    if (btn.dataset.lang) {
      this._setLang(btn.dataset.lang);
    } else if (btn.id === "refresh") {
      this._load(true);
    } else if (btn.id === "save-settings") {
      this._saveSettings();
    } else if (btn.id === "reset-settings") {
      this._draft = null;
      this._settingsMsg = "";
      this._error = "";
      this._render();
    } else if (btn.dataset.daynav !== undefined) {
      if (btn.dataset.daynav === "today") this._dayDate = null;
      else this._shiftDay(Number(btn.dataset.daynav));
      this._fetchDay();
    } else if (btn.id === "more-unknown") {
      this._unknownLimit += 20;
      this._render();
    } else if (btn.id === "clear-unknown") {
      this._clearUnknown();
    } else if (btn.classList.contains("range")) {
      this._statsDays = Number(btn.dataset.days) || 30;
      this._fetchStats();
      this._render();
    } else if (btn.classList.contains("view")) {
      this._statsView = btn.dataset.view === "table" ? "table" : "chart";
      this._render();
    } else if (btn.id === "add") {
      this._editing = { face_id: "", name: "", old_face_id: "" };
      this._render("face-id");
    } else if (btn.classList.contains("tab")) {
      this._tab = btn.dataset.tab;
      this._editing = null;
      this._unknownLimit = 20;
      this._settingsMsg = "";
      this._render();
      if (this._tab === "stats") this._fetchStats();
      if (this._tab === "day") this._fetchDay();
    } else if (btn.classList.contains("edit")) {
      const face = this._entry()?.faces.find(f => f.face_id === btn.dataset.id);
      if (face) {
        this._editing = { ...face, old_face_id: face.face_id };
        this._render("face-name");
      }
    } else if (btn.classList.contains("delete")) {
      this._deleteFace(btn.dataset.id);
    } else if (btn.classList.contains("add-unknown")) {
      this._editing = { face_id: btn.dataset.id, name: "", old_face_id: "" };
      this._tab = "known";
      this._render("face-name");
    } else if (btn.classList.contains("forget")) {
      this._forgetUnknown(btn.dataset.id);
    } else if (btn.id === "save") {
      this._saveFace();
    } else if (btn.id === "cancel") {
      this._editing = null;
      this._error = "";
      this._render();
    }
  }

  _onInput(e) {
    const t = e.target;
    if (t?.dataset?.set) {
      const entry = this._entry();
      if (!entry) return;
      if (!this._draft) this._draft = this._settingsOf(entry);
      this._draft[t.dataset.set] = t.type === "checkbox" ? t.checked : t.value;
      this._settingsMsg = "";
      return;
    }
    if (!this._editing || !t) return;
    if (t.id === "face-id") this._editing.face_id = t.value;
    else if (t.id === "face-name") this._editing.name = t.value;
  }

  _onChange(e) {
    if (e.target?.dataset?.set && e.target.type === "checkbox") {
      this._onInput(e);
      return;
    }
    if (e.target?.id === "day-date") {
      this._dayDate = e.target.value || null;
      this._fetchDay();
      return;
    }
    if (e.target?.id === "camera") {
      this._entryId = e.target.value;
      this._editing = null;
      this._stats = null;
      this._dayData = null;
      this._draft = null;
      this._unknownLimit = 20;
      this._render();
      if (this._tab === "stats") this._fetchStats();
      if (this._tab === "day") this._fetchDay();
    }
  }

  async _saveFace() {
    if (this._saving) return;
    const idInput = this.shadowRoot.querySelector("#face-id");
    const nameInput = this.shadowRoot.querySelector("#face-name");
    const id = (idInput?.value ?? this._editing?.face_id ?? "").trim();
    const name = (nameInput?.value ?? this._editing?.name ?? "").trim();

    if (!/^\d+$/.test(id || "")) {
      this._error = this._t("errFaceId");
      this._render();
      return;
    }
    if (!name) {
      this._error = this._t("errName");
      this._render();
      return;
    }

    this._saving = true;
    const saveBtn = this.shadowRoot.querySelector("#save");
    if (saveBtn) saveBtn.disabled = true;
    try {
      await this._ws({
        type: "tapo_c260_face/save_face",
        entry_id: this._entryId,
        face_id: id,
        name,
        old_face_id: this._editing?.old_face_id || ""
      });
      this._editing = null;
      this._error = "";
      this._saving = false;
      await this._load(true);
    } catch (err) {
      this._saving = false;
      this._error = err?.message || String(err);
      this._render();
    }
  }

  async _deleteFace(faceId) {
    if (!confirm(this._t("cfDelete", { id: faceId }))) return;
    try { await this._ws({ type: "tapo_c260_face/delete_face", entry_id: this._entryId, face_id: faceId }); await this._load(true); }
    catch (err) { this._error = err?.message || String(err); this._render(); }
  }

  async _forgetUnknown(faceId) {
    if (!confirm(this._t("cfForget", { id: faceId }))) return;
    try { await this._ws({ type: "tapo_c260_face/forget_unknown", entry_id: this._entryId, face_id: faceId }); await this._load(true); }
    catch (err) { this._error = err?.message || String(err); this._render(); }
  }

  async _clearUnknown() {
    const n = this._entry()?.unknown_faces?.length || 0;
    if (!confirm(this._t("cfClear", { n }))) return;
    try {
      await this._ws({ type: "tapo_c260_face/clear_unknown", entry_id: this._entryId });
      this._unknownLimit = 20;
      await this._load(true);
    } catch (err) { this._error = err?.message || String(err); this._render(); }
  }
}

if (!customElements.get(PANEL_TAG)) {
  customElements.define(PANEL_TAG, TapoC260FaceManager);
}
