import os
from typing import Dict, List

from PIL import Image, ImageDraw


class MapEngine:
    """Map overlay system for locations, ink, and veil nodes."""

    def __init__(self, base_map_path: str = "maps/base_map.png"):
        self.base_map_path = base_map_path
        self.overlay_dir = "maps/overlays"
        os.makedirs(self.overlay_dir, exist_ok=True)

    async def generate_overlay(
        self,
        world_id: str,
        cycle_id: str,
        locations: List[Dict],
        map_inks: List[Dict],
        veil_nodes: List[Dict],
    ) -> str:
        if not os.path.exists(self.base_map_path):
            img = Image.new("RGB", (1000, 800), color="#f0e6d2")
        else:
            img = Image.open(self.base_map_path).convert("RGB")

        draw = ImageDraw.Draw(img)

        for loc in locations:
            if loc.get("x") is None or loc.get("y") is None:
                continue
            x, y = loc["x"], loc["y"]
            color = self._get_location_color(loc.get("type", "ruin"))
            draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=color, outline="black", width=2)
            draw.text((x + 12, y - 8), str(loc.get("name", "Unknown")), fill="black")

        for ink in map_inks:
            loc = next((item for item in locations if item.get("id") == ink.get("location_id")), None)
            if not loc or loc.get("x") is None or loc.get("y") is None:
                continue
            x, y = loc["x"], loc["y"]
            draw.ellipse([x - 12, y - 12, x + 12, y + 12], outline="#8B4513", width=3)
            player = str(ink.get("player_name", "P"))[:2]
            draw.text((x + 15, y - 20), f"{player}'s ink", fill="#8B4513")

        for node in veil_nodes:
            loc = next((item for item in locations if item.get("id") == node.get("location_id")), None)
            if not loc or loc.get("x") is None or loc.get("y") is None:
                continue
            x, y = loc["x"], loc["y"]
            level = float(node.get("silence_level", 0.0))
            draw.ellipse([x - 20, y - 20, x + 20, y + 20], outline="#4B0082", width=2)
            if level > 2:
                draw.ellipse([x - 30, y - 30, x + 30, y + 30], outline="#4B0082", width=1)

        overlay_path = f"{self.overlay_dir}/{world_id}_{cycle_id}.png"
        img.save(overlay_path)
        return overlay_path

    def _get_location_color(self, location_type: str) -> str:
        colors = {
            "village": "#90EE90",
            "bog": "#8B4513",
            "ruin": "#808080",
            "road": "#D2B48C",
            "forest": "#228B22",
            "mountain": "#A9A9A9",
            "city": "#FFD700",
            "dungeon": "#800000",
            "claimed": "#ADD8E6",
        }
        return colors.get(location_type, "#FFFFFF")

    async def claim_unlabeled_area(self, world_id: str, x: float, y: float, name: str) -> dict:
        return {
            "id": None,
            "world_id": world_id,
            "name": name,
            "x": x,
            "y": y,
            "type": "claimed",
            "ecology_json": {},
            "arcanology_json": {},
            "history_json": {},
        }
