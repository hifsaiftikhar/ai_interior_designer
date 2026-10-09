import requests

url = "https://lushly-sputter-uneasily.ngrok-free.dev/generate"

files = {"file": open("test_images/room.jpg", "rb")}
data = {"generation_prompt": "A warm cozy room minimal bed on same position sidetable with drawers and lamp of a good size not too large and wardrobe along wall or any good good lightning and paint that will look cozy minimal and ...a large freestanding wardrobe with visible wooden doors and brass handles, clearly defined as a piece of bedroom storage furniture, positioned against the wall...."}

response = requests.post(url, files=files, data=data)
result = response.json()

if result["status"] == "success":
    import base64
    with open("generated_output.png", "wb") as f:
        f.write(base64.b64decode(result["image_base64"]))
    print("Saved generated_output.png")
else:
    print("Error:", result)