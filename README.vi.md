# Tapo C260 Face Recognition cho Home Assistant

[🇬🇧 English](README.md) · 🇻🇳 Tiếng Việt

Custom integration cho Home Assistant, đọc **sự kiện nhận diện khuôn mặt của camera TP-Link Tapo C260** qua mạng nội bộ và biến chúng thành entity, event và một trang quản lý ("Face Manager"): ai xuất hiện, lúc nào, bao nhiêu lần, ai là người lạ.

> **Không chính thức.** Không liên kết hay được TP-Link xác nhận. Integration dùng API nội bộ của camera với *tài khoản camera* (Cloud Password). Tự chịu rủi ro khi sử dụng.

## Tính năng

- Poll camera lấy event khuôn mặt; ánh xạ **Face ID → tên** (camera chỉ biết ID).
- Người lạ được ghi nhận tự động, sau đó có thể đặt tên cho một ID lạ.
- **Nhiều khuôn mặt trong một event** được xử lý riêng từng người (ví dụ người quen đi cùng người lạ).
- Chống trùng event, có cooldown cho người quen.
- Trang **Face Manager** ở sidebar (có nút chuyển Việt / Anh):
  - danh sách người quen / người lạ, thêm / đổi tên / xoá;
  - **lịch sử ngày** – ai xuất hiện lúc nào, lần đầu và gần nhất trong ngày;
  - **thống kê** – người lạ hôm nay / 7 / 30 ngày, biểu đồ, top người lạ, số lần từng người;
  - **sức khoẻ integration** – poll thành công gần nhất, thời gian phản hồi, lỗi, chế độ kết nối, số event bị dedup;
  - **cài đặt** – polling, dedup, giới hạn lưu trữ, bật/tắt và đổi tên sidebar.
- Đổi tên một người áp dụng cho **toàn bộ record cũ** (lịch sử lưu theo Face ID, tên được tra lúc hiển thị).
- Giới hạn lưu trữ: giữ thống kê/người lạ tối đa N ngày và tối đa M người lạ.
- Chạy **song song với Tapo-Control** bằng cách dùng lại controller của nó cho cùng camera, để hai integration không tranh session với camera (xem [Chế độ hoạt động](#chế-độ-hoạt-động)).
- Có luồng đăng nhập lại khi camera từ chối đăng nhập.

## Yêu cầu

- Home Assistant **2026.9.4** trở lên (phiên bản tối thiểu được khai báo).
- Camera Tapo **C260** đã bật nhận diện khuôn mặt trong app Tapo, và tài khoản camera (username + Cloud Password).
- Tuỳ chọn: integration [Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control) cho cùng camera.

## Môi trường đã thử nghiệm

- Camera: Tapo C260 với firmware `1.2.3 Build 260805 Rel.20715n` và `1.3.2 Build 260902 Rel.25093n`.
- Tapo-Control (Tapo: Cameras Control): phiên bản mới nhất tại thời điểm kiểm thử.

## Cài đặt

### HACS (custom repository)

1. HACS → ⋮ → **Custom repositories** → thêm `https://github.com/quangtienhn/tapo-c260-face`, loại **Integration**.
2. Tải **Tapo C260 Face Recognition**, rồi restart Home Assistant.
3. Settings → Devices & services → **Add integration** → *Tapo C260 Face Recognition*.

### Thủ công

Chép thư mục `custom_components/tapo_c260_face` vào `config/custom_components/` của Home Assistant rồi restart.

## Thiết lập

1. Settings → Devices & services → **Add integration** → *Tapo C260 Face Recognition*.
2. Điền form cấu hình (form giống nhau ở cả hai chế độ hoạt động — xem [Chế độ hoạt động](#chế-độ-hoạt-động)):

   | Trường | Nhập gì |
   |---|---|
   | **Host** | Địa chỉ IP nội bộ của Tapo C260, ví dụ `192.168.1.188`. |
   | **Username** | Tên tài khoản camera đã cấu hình trên camera để kết nối cục bộ / bên thứ ba. Đây không phải email tài khoản Tapo Cloud của bạn. |
   | **Cloud Password** | Cloud Password của camera cho tài khoản đó. Integration chỉ dùng nó trong luồng đăng nhập challenge/response nội bộ của camera (`cnonce`/`nonce`, `digest_passwd`; mật khẩu được băm thành digest, không bao giờ gửi dạng plain text). Nó được lưu trong config entry của Home Assistant như thông tin đăng nhập của mọi integration khác. |

3. Đăng nhập được kiểm tra với camera ngay khi thêm. Nếu sau này camera từ chối, luồng đăng nhập lại sẽ hỏi lại username và Cloud Password.
4. Code của integration không yêu cầu bước chuẩn bị nào khác (không có nút bật tương thích nào bên trong integration này): nó kết nối thẳng tới API nội bộ của camera tại IP đã nhập, dùng thông tin tài khoản camera ở trên.
5. Không nhập thông tin đăng nhập vào file README, GitHub issue, URL, log hay ảnh chụp công khai.

Sau đó mở **Face Manager** (sidebar hoặc `/tapo_c260_face`), xem tab *Unknown* sau khi camera thấy ai đó, bấm **Thêm người** để đặt tên cho Face ID đó.

## Ảnh minh họa

![Sensors](docs/images/sensors.jpg)
*Các sensor của thiết bị: khuôn mặt gần nhất, số người quen/người lạ, trạng thái phát hiện người lạ và bộ đếm sức khỏe.*

![Event và chẩn đoán](docs/images/event-diagnostic.jpg)
*Trang thiết bị: một event `face_unknown` cùng các sensor chẩn đoán. Ở đây Connection Mode là `shared`, tức chế độ dùng chung controller (xem bên dưới).*

![Face Manager – người quen](docs/images/face-manager-known.jpg)
*Face Manager, tab Known: ánh xạ Face ID → tên, banner sức khỏe và chế độ kết nối.*

![Face Manager – người lạ](docs/images/face-manager-unknown.jpg)
*Face Manager, tab Unknown: các Face ID lạ kèm lần thấy đầu/cuối và số lần; bấm Add person để đặt tên.*

![Face Manager – thống kê](docs/images/face-manager-statistics.jpg)
*Face Manager, tab Statistics: số người lạ, biểu đồ xuất hiện theo ngày và người lạ hay gặp nhất.*

![Face Manager – cài đặt](docs/images/face-manager-settings.jpg)
*Face Manager, tab Settings: polling/dedup, giới hạn lưu trữ và tùy chọn hiển thị sidebar.*

![Menu tùy chọn](docs/images/options-menu.jpg)
*Menu tùy chọn của integration (Configure → Management): quản lý Face ID, polling, lưu trữ và sidebar.*

## Entity (mỗi camera)

| Entity | Mô tả |
|---|---|
| `sensor.…_face_name`, `…_face_id` | Khuôn mặt gần nhất (trong một event ưu tiên người quen). |
| `sensor.…_last_seen` | Giờ camera của event gần nhất. |
| `sensor.…_known_faces`, `…_unknown_faces` | Số ID đã khai báo / đã phát hiện. |
| `sensor.…_unknown_today`, `…_last_unknown_seen` | Người lạ hôm nay / lần cuối thấy người lạ. |
| `binary_sensor.…_face_recognized` | Khuôn mặt gần nhất là người quen. |
| `binary_sensor.…_stranger_detected` | Bật khi có event người lạ **mới**, tự tắt sau N giây (mặc định 30). |
| `event.…_face_event` | `face_recognized` / `face_unknown` kèm `face_id`, `name`, `event_time`, … |
| `binary_sensor.…_camera_connection`, `sensor.…_polling_errors`, `…_connection_mode`, `…_dedup_skipped` | Sức khoẻ (luôn available, kể cả khi poll lỗi). |
| `…_last_successful_poll`, `…_response_time` | Sức khoẻ, mặc định tắt (đổi mỗi lần poll). |

Bus event `tapo_c260_face_detected` được bắn cho mỗi khuôn mặt mới, kèm `face_id`, `name`, `recognized`, `event_time`, `camera`, `event_face_ids`, …

> Lưu ý: với người lạ, sensor `Face Name` trả về `Stranger` (bản ≤ 0.1.7.0 trả `Người lạ` — cập nhật automation nào đang so sánh state).

## Ví dụ automation

```yaml
automation:
  - alias: Người lạ trước cửa
    triggers:
      - trigger: state
        entity_id: binary_sensor.CAMERA_stranger_detected
        to: "on"
    actions:
      - action: notify.notify
        data:
          message: "Phát hiện người lạ"

  - alias: Người quen về nhà
    triggers:
      - trigger: event
        event_type: tapo_c260_face_detected
        event_data:
          recognized: true
    actions:
      - action: notify.notify
        data:
          message: "{{ trigger.event.data.name }} vừa xuất hiện"
```

## Chế độ hoạt động

Form cấu hình giống nhau ở cả hai chế độ: đăng nhập luôn được kiểm tra với camera khi tạo entry. Khác nhau ở cách mỗi lần poll truy vấn camera sau đó.

|  | Chế độ độc lập | Chế độ dùng chung controller |
|---|---|---|
| Cần cài Tapo-Control | Không | Có, với một entry cho cùng IP camera |
| Truy vấn camera qua | Session riêng của integration | Controller sẵn có của Tapo-Control (`searchDetectionList`) |
| Phiên đăng nhập riêng tới camera | Có | Không — dùng lại controller đã xác thực của Tapo-Control và không tự đăng nhập khi ở chế độ này |
| Vẫn cần nhập thông tin đăng nhập khi cài | Có | Có (kiểm tra một lần lúc cài) |
| Entry Tapo-Control tồn tại nhưng đang khởi động | n/a | Chờ mà không tự đăng nhập; sức khỏe báo `waiting` cho tới khi controller sẵn sàng |
| Entry Tapo-Control bị tắt / lỗi / không có controller dùng được | n/a | Rơi về session riêng |
| Chỉnh sửa cấu hình Tapo-Control của bạn | Không | Không |

### Chế độ độc lập (Standalone)

Không cần Tapo-Control. Integration tự thực hiện đăng nhập bảo mật nội bộ của camera (challenge/response với `cnonce`/`nonce`, `digest_passwd`, khóa phiên `lsk`/`ivb`, bằng bản triển khai asyncio riêng) và poll `searchDetectionList` qua session mã hóa riêng. Ở chế độ này nó không dùng chung phiên đăng nhập hay controller nào của Tapo-Control, vì không có gì để dùng chung.

### Chế độ dùng cùng Tapo-Control (Shared-controller)

Khi tồn tại entry Tapo-Control cho cùng IP camera và controller của nó đã sẵn sàng, integration gọi `searchDetectionList` **qua controller đó** thay vì tự đăng nhập, để hai integration không tranh session với camera. Khi entry Tapo-Control còn đang khởi động, integration chờ (trả về trạng thái rỗng vô hại để setup hoàn tất rồi thử lại ở lần poll sau) thay vì mở session thứ hai. Nếu entry Tapo-Control bị tắt, lỗi, hoặc đã load nhưng không có controller dùng được, integration ghi warning và dùng session riêng. Chế độ này chỉ *đọc* đối tượng controller lúc chạy; không thay thế, cấu hình lại hay sửa đổi gì trong setup Tapo-Control của bạn. Cách này dựa vào cấu trúc dữ liệu nội bộ của Tapo-Control nên có thể hỏng khi họ thay đổi (đã thử nghiệm với phiên bản Tapo-Control mới nhất tại thời điểm kiểm thử).

## Dữ liệu và quyền riêng tư

Mọi thứ nằm cục bộ. Thông tin đăng nhập camera lưu trong config entry của Home Assistant (như mọi integration). Ánh xạ Face ID → tên lưu trong options của config entry; danh sách người lạ và lịch sử lưu ở `.storage/tapo_c260_face.*`. Không lưu khuôn mặt hay hình ảnh – chỉ lưu các ID số mà camera báo.

## Giới hạn đã biết

- Mới thử nghiệm trên một model (C260) với firmware `1.2.3 Build 260805 Rel.20715n` và `1.3.2 Build 260902 Rel.25093n`.
- Thống kê và lịch sử theo giờ chỉ có từ phiên bản bổ sung chúng.
- Tên entity là tiếng Anh; trang Face Manager và config flow có tiếng Anh và tiếng Việt.

## Ghi nhận

Quy trình đăng nhập an toàn cục bộ của camera (challenge/response với `cnonce`/`nonce`, `digest_passwd`, khoá phiên `lsk`/`ivb`) theo giao thức đã được dự án mã nguồn mở [pytapo](https://github.com/JurajNyiri/pytapo) (MIT, © Juraj Nyíri) mô tả. Repo này có bản triển khai asyncio/aiohttp riêng và không đóng gói file mã nguồn nào của pytapo hay Tapo-Control. Chế độ dùng chung (tuỳ chọn) làm việc với đối tượng controller của [Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control) (Apache-2.0) lúc chạy. Cảm ơn các dự án đó.

## Giấy phép

[MIT](LICENSE)
