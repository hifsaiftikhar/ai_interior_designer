import { useState } from "react";
import ImageUploader from "./ImageUploader";
import "../styles/designer.css";

const API_URL = "http://127.0.0.1:8000";

function DesignStudio() {
  const [selectedImage, setSelectedImage] = useState(null);

  const [style, setStyle] = useState("Modern Minimalist");
  const [budget, setBudget] = useState("Medium");
  const [colors, setColors] = useState(["Beige", "White"]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const availableColors = [
    "Beige",
    "White",
    "Brown",
    "Green",
    "Blue",
    "Black",
  ];

  const toggleColor = (color) => {
    setColors((current) => {
      if (current.includes(color)) {
        return current.filter((item) => item !== color);
      }

      if (current.length >= 3) {
        return current;
      }

      return [...current, color];
    });
  };

  const getBudgetNumber = () => {
    if (budget === "Low") return 500;
    if (budget === "Medium") return 1500;
    return 3000;
  };

  const handleGenerate = async () => {
    if (!selectedImage) {
      setError("Please upload a room image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();

      formData.append("file", selectedImage);
      formData.append("style", style);
      formData.append("budget", budget);
      formData.append("budget_num", getBudgetNumber());
      formData.append("preferred_colors", colors.join(","));

      // STEP 1: Create generation job
      const response = await fetch(`${API_URL}/design`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || "Design generation request failed."
        );
      }

      const data = await response.json();

      console.log("Design API response:", data);

      setResult(data);

      // STEP 2: Get job ID
      const jobId = data.job_id;

      // STEP 3: Wait for Colab GPU generation
      let completedResult = null;

      for (let attempt = 0; attempt < 60; attempt++) {
        await new Promise((resolve) => setTimeout(resolve, 5000));

        const jobResponse = await fetch(
          `${API_URL}/job/${jobId}`
        );

        if (!jobResponse.ok) {
          throw new Error("Could not check generation status.");
        }

        const jobData = await jobResponse.json();

        console.log("Generation status:", jobData);

        if (jobData.status === "completed") {
          completedResult = jobData;
          break;
        }

        if (jobData.status === "failed") {
          throw new Error(
            jobData.error || "Image generation failed."
          );
        }
      }

      if (!completedResult) {
        throw new Error(
          "Image generation is taking longer than expected."
        );
      }

      // STEP 4: Add generated image to result
      
const imageResponse = await fetch(
  `${API_URL}/job/${jobId}/image`
);

if (!imageResponse.ok) {
  throw new Error("Generated image could not be loaded.");
}

const imageBlob = await imageResponse.blob();
const imageUrl = URL.createObjectURL(imageBlob);

setResult({
  ...data,
  generation_status: "completed",
  image_url: imageUrl,
});


    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Something went wrong while connecting to the AI designer."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="design-studio" id="design-studio">

      <div className="studio-heading">

        <p className="section-label">
          04 — DESIGN STUDIO
        </p>

        <h2>
          Make the
          <br />
          <em>space yours.</em>
        </h2>

        <p>
          Upload your room and tell us what you have in mind.
          Our AI will take care of the rest.
        </p>

      </div>

      <div className="studio-grid">

        {/* IMAGE UPLOAD */}

        <div className="studio-upload">

          <div className="studio-label">
            <span>01</span>
            <span>YOUR ROOM</span>
          </div>

          <ImageUploader
            onImageSelect={(file) => {
              setSelectedImage(file);
              setError("");
            }}
          />

        </div>


        {/* PREFERENCES */}

        <div className="studio-form">

          <div className="studio-label">
            <span>02</span>
            <span>YOUR PREFERENCES</span>
          </div>


          {/* STYLE */}

          <div className="form-group">

            <label>
              Interior style
            </label>

            <div className="option-grid">

              {[
                "Modern Minimalist",
                "Classic",
                "Scandinavian",
                "Industrial",
              ].map((option) => (

                <button
                  key={option}
                  type="button"
                  className={
                    style === option
                      ? "option active"
                      : "option"
                  }
                  onClick={() => setStyle(option)}
                >
                  {option}
                </button>

              ))}

            </div>

          </div>


          {/* BUDGET */}

          <div className="form-group">

            <label>
              Budget
            </label>

            <div className="budget-options">

              {[
                "Low",
                "Medium",
                "High",
              ].map((option) => (

                <button
                  key={option}
                  type="button"
                  className={
                    budget === option
                      ? "budget-option active"
                      : "budget-option"
                  }
                  onClick={() => setBudget(option)}
                >
                  {option}
                </button>

              ))}

            </div>

          </div>


          {/* COLORS */}

          <div className="form-group">

            <label>

              Preferred colors

              <span className="color-limit">
                {colors.length}/3
              </span>

            </label>

            <div className="color-options">

              {availableColors.map((color) => (

                <button
                  key={color}
                  type="button"
                  className={
                    colors.includes(color)
                      ? "color-option active"
                      : "color-option"
                  }
                  onClick={() => toggleColor(color)}
                >

                  <span
                    className={`color-dot ${color
                      .toLowerCase()
                      .replace(" ", "-")}`}
                  />

                  {color}

                </button>

              ))}

            </div>

          </div>


          {/* ERROR */}

          {error && (
            <div className="designer-error">
              {error}
            </div>
          )}


          {/* GENERATE */}

          <button
            type="button"
            className="generate-button"
            onClick={handleGenerate}
            disabled={loading}
          >

            <span>
              {loading
                ? "AI is designing your room..."
                : "Generate my room"}
            </span>

            <span>
              {loading ? "..." : "→"}
            </span>

          </button>

        </div>

      </div>


      {/* AI RESPONSE */}

      {result && (

        <div className="design-response">

          <div className="studio-label">

            <span>03</span>

            <span>
              AI DESIGN PLAN
            </span>

          </div>


          <div className="response-grid">


            {/* JOB */}

            <div>

              <p className="response-label">
                JOB
              </p>

              <p className="job-id">
                {result.job_id}
              </p>

              <p className="response-status">
                {result.generation_status}
              </p>

            </div>


            {/* ROOM ANALYSIS */}

            <div>

              <p className="response-label">
                ROOM ANALYSIS
              </p>

              <p>
                {result.room_analysis?.room_type}
              </p>

              <p className="response-muted">
                Style detected:{" "}
                {result.room_analysis?.style}
              </p>

            </div>


            {/* AI DESIGN */}

            <div>

              <p className="response-label">
                AI DESIGN
              </p>

              <p>
                {result.design_plan?.design_style}
              </p>

              <p className="response-muted">
                {result.design_plan?.color_palette?.join(
                  " · "
                )}
              </p>

            </div>

          </div>


          {/* GENERATED IMAGE */}

          {result.image_url && (
  <div className="generated-result">
    <p className="response-label">
      GENERATED ROOM
    </p>

    <img
      src={result.image_url}
      alt="AI redesigned room"
      className="generated-room-image"
    />
  </div>
)}

        </div>

      )}

    </section>
  );
}

export default DesignStudio;