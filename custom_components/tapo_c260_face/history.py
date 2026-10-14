"""Kho lịch sử xuất hiện theo ngày cho Face Manager.

Lịch sử lưu theo **Face ID của camera**, không lưu tên. Tên người được tra từ
danh sách người quen lúc hiển thị, nên đổi tên một người tự áp dụng cho toàn bộ
record cũ (và đặt tên cho một ID lạ thì các lần xuất hiện cũ của nó chuyển từ
"người lạ" sang người đó).

Dạng dữ liệu (JSON, lưu bằng homeassistant.helpers.storage.Store):

    {
      "days": {"2026-10-11": {"8589934594": 3, "123": 1}},
      "last_seen": {"8589934594": "2026-10-11T03:04:05+00:00"}
    }

Module này không phụ thuộc Home Assistant để dễ kiểm thử.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta, tzinfo
from typing import Any

MAX_RANGE_DAYS = 365
# Số mốc giờ tối đa lưu cho mỗi (ngày, Face ID); quá thì giữ các mốc đầu ngày.
MAX_TIMES_PER_DAY_ID = 500


def _valid_day(value: Any) -> bool:
    try:
        date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return False
    return True


class FaceHistory:
    """Số lần xuất hiện của từng Face ID theo ngày."""

    def __init__(self) -> None:
        self.days: dict[str, dict[str, int]] = {}
        self.last_seen: dict[str, str] = {}
        # Mốc giờ (epoch giây, UTC) từng lần xuất hiện: {ngày: {face_id: [ts,...]}}.
        self.times: dict[str, dict[str, list[int]]] = {}

    # ------------------------------------------------------------------ io
    @classmethod
    def from_dict(cls, data: Any) -> FaceHistory:
        """Đọc dữ liệu đã lưu; bỏ qua mọi phần tử sai định dạng."""
        history = cls()
        if not isinstance(data, Mapping):
            return history

        days = data.get("days")
        if isinstance(days, Mapping):
            for day, bucket in days.items():
                if not _valid_day(day) or not isinstance(bucket, Mapping):
                    continue
                clean: dict[str, int] = {}
                for face_id, count in bucket.items():
                    try:
                        number = int(count)
                    except (TypeError, ValueError):
                        continue
                    if number > 0:
                        clean[str(face_id)] = number
                if clean:
                    history.days[str(day)] = clean

        times = data.get("times")
        if isinstance(times, Mapping):
            for day, bucket in times.items():
                if not _valid_day(day) or not isinstance(bucket, Mapping):
                    continue
                clean_t: dict[str, list[int]] = {}
                for face_id, values in bucket.items():
                    if not isinstance(values, (list, tuple)):
                        continue
                    stamps = []
                    for value in values:
                        try:
                            stamps.append(int(value))
                        except (TypeError, ValueError):
                            continue
                    if stamps:
                        clean_t[str(face_id)] = sorted(stamps)[:MAX_TIMES_PER_DAY_ID]
                if clean_t:
                    history.times[str(day)] = clean_t

        last_seen = data.get("last_seen")
        if isinstance(last_seen, Mapping):
            history.last_seen = {
                str(face_id): str(value)
                for face_id, value in last_seen.items()
                if value
            }
        return history

    def to_dict(self) -> dict[str, Any]:
        return {
            "days": {day: dict(bucket) for day, bucket in self.days.items()},
            "last_seen": dict(self.last_seen),
            "times": {
                day: {fid: list(v) for fid, v in bucket.items()}
                for day, bucket in self.times.items()
            },
        }

    # ------------------------------------------------------------- mutation
    def record(
        self, face_id: str, day: date, seen_iso: str, at: datetime | None = None
    ) -> None:
        """Ghi một lần xuất hiện của `face_id` vào ngày `day` (giờ địa phương)."""
        face_id = str(face_id)
        bucket = self.days.setdefault(day.isoformat(), {})
        bucket[face_id] = bucket.get(face_id, 0) + 1
        previous = self.last_seen.get(face_id)
        if previous is None or seen_iso > previous:
            self.last_seen[face_id] = seen_iso
        if at is not None:
            stamps = self.times.setdefault(day.isoformat(), {}).setdefault(face_id, [])
            if len(stamps) < MAX_TIMES_PER_DAY_ID:
                stamps.append(int(at.timestamp()))
                stamps.sort()

    def has(self, face_id: str) -> bool:
        face_id = str(face_id)
        return face_id in self.last_seen or any(
            face_id in bucket for bucket in self.days.values()
        )

    def prune(self, keep_days: int, today: date) -> bool:
        """Xoá các ngày cũ hơn `keep_days` (tính cả hôm nay). True nếu có đổi."""
        keep_days = max(1, int(keep_days))
        cutoff = (today - timedelta(days=keep_days - 1)).isoformat()
        changed = False
        for day in [d for d in self.days if d < cutoff]:
            del self.days[day]
            changed = True
        for day in [d for d in self.times if d < cutoff]:
            del self.times[day]
        present = {fid for bucket in self.days.values() for fid in bucket}
        for face_id in [f for f in self.last_seen if f not in present]:
            del self.last_seen[face_id]
            changed = True
        return changed

    def purge(self, face_id: str) -> bool:
        """Xoá toàn bộ lịch sử của một Face ID."""
        return self.purge_where(lambda fid: fid == str(face_id))

    def purge_where(self, predicate: Callable[[str], bool]) -> bool:
        """Xoá lịch sử của mọi Face ID thoả `predicate`."""
        changed = False
        for day in list(self.days):
            bucket = self.days[day]
            for face_id in [f for f in bucket if predicate(f)]:
                del bucket[face_id]
                changed = True
            if not bucket:
                del self.days[day]
        for day in list(self.times):
            bucket_t = self.times[day]
            for face_id in [f for f in bucket_t if predicate(f)]:
                del bucket_t[face_id]
            if not bucket_t:
                del self.times[day]
        for face_id in [f for f in self.last_seen if predicate(f)]:
            del self.last_seen[face_id]
            changed = True
        return changed

    def merge(self, old_id: str, new_id: str) -> bool:
        """Gộp lịch sử của `old_id` vào `new_id` (khi người dùng đổi Face ID)."""
        old_id, new_id = str(old_id), str(new_id)
        if old_id == new_id:
            return False
        changed = False
        for bucket in self.days.values():
            count = bucket.pop(old_id, 0)
            if count:
                bucket[new_id] = bucket.get(new_id, 0) + count
                changed = True
        for bucket_t in self.times.values():
            moved = bucket_t.pop(old_id, None)
            if moved:
                bucket_t[new_id] = sorted(
                    (bucket_t.get(new_id, []) + moved)[:MAX_TIMES_PER_DAY_ID]
                )
        old_seen = self.last_seen.pop(old_id, None)
        if old_seen:
            changed = True
            current = self.last_seen.get(new_id)
            if current is None or old_seen > current:
                self.last_seen[new_id] = old_seen
        return changed

    # --------------------------------------------------------------- queries
    def summary(self, face_id: str) -> dict[str, Any] | None:
        """Tổng số lần, ngày đầu và lần cuối của một Face ID (None nếu không có)."""
        face_id = str(face_id)
        total = 0
        first_day: str | None = None
        for day in sorted(self.days):
            count = self.days[day].get(face_id, 0)
            if count:
                total += count
                if first_day is None:
                    first_day = day
        if not total:
            return None
        return {
            "count": total,
            "first_day": first_day,
            "last_seen": self.last_seen.get(face_id),
        }

    def day_view(
        self, known: Mapping[str, str], day: date, tz: tzinfo
    ) -> dict[str, Any]:
        """Ai xuất hiện lúc nào trong một ngày (giờ theo `tz`).

        Người quen gộp theo tên (nhiều Face ID của cùng một người thành một dòng);
        người lạ mỗi Face ID một dòng.
        """
        key = day.isoformat()
        counts = self.days.get(key, {})
        stamps = self.times.get(key, {})
        groups: dict[str, dict[str, Any]] = {}
        for face_id in set(counts) | set(stamps):
            name = known.get(face_id)
            gkey = f"k:{name}" if name else f"u:{face_id}"
            group = groups.setdefault(
                gkey,
                {
                    "name": name,
                    "known": bool(name),
                    "face_ids": [],
                    "count": 0,
                    "_ts": [],
                },
            )
            group["face_ids"].append(face_id)
            group["count"] += counts.get(face_id, 0)
            group["_ts"].extend(stamps.get(face_id, []))

        people = []
        for group in groups.values():
            ts = sorted(group.pop("_ts"))
            labels = [datetime.fromtimestamp(t, tz).strftime("%H:%M:%S") for t in ts]
            group["face_ids"].sort()
            group["times"] = labels
            group["first"] = labels[0] if labels else None
            group["last"] = labels[-1] if labels else None
            # Số lần ghi trước khi có mốc giờ (dữ liệu bản cũ) = count - len(times).
            group["untimed"] = max(0, group["count"] - len(labels))
            people.append(group)
        people.sort(
            key=lambda p: (
                p["first"] is None,
                p["first"] or "",
                (p["name"] or "~" + ",".join(p["face_ids"])).lower(),
            )
        )
        return {
            "date": key,
            "available_days": sorted(self.days),
            "people": people,
        }

    def stats(
        self,
        known: Mapping[str, str],
        today: date,
        range_days: int,
        top_n: int = 10,
    ) -> dict[str, Any]:
        """Thống kê. `known` là ánh xạ Face ID → tên *hiện tại*.

        Face ID có trong `known` là người quen, còn lại là người lạ. Vì phân loại
        và tên đều lấy lúc tính, đổi tên / đặt tên cho ID lạ áp dụng cho cả lịch sử.
        """
        range_days = max(1, min(int(range_days), MAX_RANGE_DAYS))
        start = today - timedelta(days=range_days - 1)

        unknown_by_day: dict[str, int] = {}
        known_by_day: dict[str, int] = {}
        per_id: dict[str, int] = {}
        days_seen: dict[str, int] = {}
        first_day_of: dict[str, str] = {}

        for day in sorted(self.days):
            for face_id, count in self.days[day].items():
                per_id[face_id] = per_id.get(face_id, 0) + count
                days_seen[face_id] = days_seen.get(face_id, 0) + 1
                first_day_of.setdefault(face_id, day)
                target = known_by_day if face_id in known else unknown_by_day
                target[day] = target.get(day, 0) + count

        daily = []
        for offset in range(range_days):
            day = (start + timedelta(days=offset)).isoformat()
            daily.append(
                {
                    "date": day,
                    "unknown": unknown_by_day.get(day, 0),
                    "known": known_by_day.get(day, 0),
                }
            )

        def window(days: int) -> int:
            first = (today - timedelta(days=days - 1)).isoformat()
            last = today.isoformat()
            return sum(n for d, n in unknown_by_day.items() if first <= d <= last)

        peak_day = None
        if unknown_by_day:
            day, count = max(unknown_by_day.items(), key=lambda item: (item[1], item[0]))
            peak_day = {"date": day, "count": count}

        unknown_ids = [fid for fid in per_id if fid not in known]
        top_unknown = [
            {
                "face_id": fid,
                "count": per_id[fid],
                "days_seen": days_seen[fid],
                "first_day": first_day_of[fid],
                "last_seen": self.last_seen.get(fid),
            }
            for fid in sorted(
                unknown_ids,
                key=lambda f: (per_id[f], self.last_seen.get(f, "")),
                reverse=True,
            )[: max(1, top_n)]
        ]

        by_name: dict[str, dict[str, Any]] = {}
        for face_id, name in known.items():
            person = by_name.setdefault(
                name, {"name": name, "face_ids": [], "count": 0, "last_seen": None}
            )
            person["face_ids"].append(face_id)
            person["count"] += per_id.get(face_id, 0)
            seen = self.last_seen.get(face_id)
            if seen and (person["last_seen"] is None or seen > person["last_seen"]):
                person["last_seen"] = seen
        persons = sorted(
            by_name.values(), key=lambda p: (-p["count"], p["name"].lower())
        )
        for person in persons:
            person["face_ids"].sort()

        return {
            "range_days": range_days,
            "today": today.isoformat(),
            "first_day": min(self.days) if self.days else None,
            "daily": daily,
            "unknown": {
                "total_events": sum(unknown_by_day.values()),
                "distinct_ids": len(unknown_ids),
                "today": window(1),
                "last_7_days": window(7),
                "last_30_days": window(30),
                "peak_day": peak_day,
                "top": top_unknown,
            },
            "known": {
                "total_events": sum(known_by_day.values()),
                "persons": persons,
            },
        }
