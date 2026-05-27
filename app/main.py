from fastapi import FastAPI

app = FastAPI(title="AI Field Companion API")

@app.get("/")
def root():
    return {"message": "AI Field Companion API is running", "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/species/{species_id}")
def get_species(species_id: int):
    species_db = {
        1: {"name": "Eucalyptus deglupta", "local_name": "Kamarere", "disease_risk": "low"},
        2: {"name": "Tectona grandis", "local_name": "Teak", "disease_risk": "medium"},
        3: {"name": "Acacia mangium", "local_name": "Mangium", "disease_risk": "low"},
    }
    if species_id not in species_db:
        return {"error": "Species not found"}
    return species_db[species_id]

@app.get("/diagnose/{condition}")
def diagnose(condition: str):
    conditions = {
        "leaf_blight": {"diagnosis": "Leaf Blight", "severity": "medium", "treatment": "Apply copper fungicide"},
        "root_rot": {"diagnosis": "Root Rot", "severity": "high", "treatment": "Improve drainage, reduce watering"},
        "healthy": {"diagnosis": "Healthy", "severity": "none", "treatment": "No action needed"},
    }
    if condition not in conditions:
        return {"error": "Condition not found"}
    return conditions[condition]
