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
- Chạy **song song với Tapo-Control** bằng cách dùng lại controller của nó cho cùng camera, để hai integration không tranh session với camera.
- Có luồng đăng nhập lại khi camera từ chối đăng nhập.

## Yêu cầu

- Home Assistant **2026.10** trở lên (phiên bản đã test).
- Camera Tapo **C260** đã bật nhận diện khuôn mặt trong app Tapo, và tài khoản camera (username + Cloud Password).
- Tuỳ chọn: integration [Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control) cho cùng camera.

## Cài đặt

### HACS (custom repository)

1. HACS → ⋮ → **Custom repositories** → thêm `https://github.com/quangtienhn/tapo-c260-face`, loại **Integration**.
2. Tải **Tapo C260 Face Recognition**, rồi restart Home Assistant.
3. Settings → Devices & services → **Add integration** → *Tapo C260 Face Recognition*.

### Thủ công

Chép thư mục `custom_components/tapo_c260_face` vào `config/custom_components/` của Home Assistant rồi restart.

## Thiết lập

Nhập IP camera, username tài khoản camera và Cloud Password. Sau đó mở **Face Manager** (sidebar hoặc `/tapo_c260_face`), xem tab *Unknown* sau khi camera thấy ai đó, bấm **Thêm người** để đặt tên cho Face ID đó.

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

## Dùng cùng Tapo-Control

Nếu có entry Tapo-Control cho cùng IP camera và controller của nó đã sẵn sàng, integration này truy vấn `searchDetectionList` **qua controller đó** và không tự đăng nhập. Khi Tapo-Control còn đang khởi động thì chờ; nếu Tapo-Control bị tắt hoặc lỗi thì dùng session riêng. Cách này dựa vào cấu trúc dữ liệu nội bộ của Tapo-Control nên có thể hỏng khi họ thay đổi (đã test với Tapo-Control 7.2.7).

## Dữ liệu và quyền riêng tư

Mọi thứ nằm cục bộ. Thông tin đăng nhập camera lưu trong config entry của Home Assistant (như mọi integration). Ánh xạ Face ID → tên lưu trong options của config entry; danh sách người lạ và lịch sử lưu ở `.storage/tapo_c260_face.*`. Không lưu khuôn mặt hay hình ảnh – chỉ lưu các ID số mà camera báo.

## Giới hạn đã biết

- Mới test trên một model (C260) và một firmware.
- Thống kê và lịch sử theo giờ chỉ có từ phiên bản bổ sung chúng.
- Tên entity là tiếng Anh; trang Face Manager và config flow có tiếng Anh và tiếng Việt.

## Ghi nhận

Quy trình đăng nhập an toàn cục bộ của camera (challenge/response với `cnonce`/`nonce`, `digest_passwd`, khoá phiên `lsk`/`ivb`) theo giao thức đã được dự án mã nguồn mở [pytapo](https://github.com/JurajNyiri/pytapo) (MIT, © Juraj Nyíri) mô tả. Repo này có bản triển khai asyncio/aiohttp riêng và không đóng gói file mã nguồn nào của pytapo hay Tapo-Control. Chế độ dùng chung (tuỳ chọn) làm việc với đối tượng controller của [Tapo-Control](https://github.com/JurajNyiri/HomeAssistant-Tapo-Control) (Apache-2.0) lúc chạy. Cảm ơn các dự án đó.

## Giấy phép

[MIT](LICENSE)
