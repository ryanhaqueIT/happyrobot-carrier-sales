from app.database import get_db


def search_loads(
    origin: str | None = None,
    destination: str | None = None,
    equipment_type: str | None = None,
    min_rate: float | None = None,
    max_rate: float | None = None,
) -> list[dict]:
    query = "SELECT * FROM loads WHERE 1=1"
    params: list = []

    if origin:
        query += " AND LOWER(origin) LIKE ?"
        params.append(f"%{origin.lower()}%")
    if destination:
        query += " AND LOWER(destination) LIKE ?"
        params.append(f"%{destination.lower()}%")
    if equipment_type:
        query += " AND LOWER(equipment_type) LIKE ?"
        params.append(f"%{equipment_type.lower()}%")
    if min_rate is not None:
        query += " AND loadboard_rate >= ?"
        params.append(min_rate)
    if max_rate is not None:
        query += " AND loadboard_rate <= ?"
        params.append(max_rate)

    query += " ORDER BY pickup_datetime ASC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_load_by_id(load_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM loads WHERE load_id = ?", (load_id,)).fetchone()
        return dict(row) if row else None
