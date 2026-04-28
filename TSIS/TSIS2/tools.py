def flood_fill(surface, x, y, fill_color):
    w, h = surface.get_size()
    if x < 0 or x >= w or y < 0 or y >= h:
        return
    target = surface.get_at((x, y))[:3]
    fc = fill_color[:3] if len(fill_color) > 3 else fill_color
    if target == fc:
        return
    stack = [(x, y)]
    visited = set()
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        if surface.get_at((cx, cy))[:3] != target:
            continue
        surface.set_at((cx, cy), fill_color)
        visited.add((cx, cy))
        stack.append((cx + 1, cy))
        stack.append((cx - 1, cy))
        stack.append((cx, cy + 1))
        stack.append((cx, cy - 1))
