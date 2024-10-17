from google.cloud import aiplatform

# Inicializar el entorno
aiplatform.init(project='prueba-tecnica-corona', location='southamerica-east1')

# Subir el modelo a Vertex AI
model = aiplatform.Model.upload(
    display_name="clf_model",
    artifact_uri="gs://bucket-prueba-corona-models/",
    serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.0-23:latest"
)

# Imprimir el nombre del recurso del modelo
print(f'Model created. Resource name: {model.resource_name}')