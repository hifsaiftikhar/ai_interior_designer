from app.vlm import analyze_room

image_path = "test_images/room.jpg"

result = analyze_room(image_path)

print(result.model_dump_json(indent=2))