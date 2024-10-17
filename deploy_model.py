from google.cloud import aiplatform

# Inicializar el entorno
aiplatform.init(project='prueba-tecnica-corona', location='southamerica-east1')

# Crear un endpoint en Vertex AI para el modelo
endpoint = aiplatform.Endpoint.create(display_name="clf_model_endpoint")

# Desplegar el modelo en el endpoint
model = aiplatform.Model(model_name="projects/prueba-tecnica-corona/locations/southamerica-east1/models/2026980472130633728")

model.deploy(
    endpoint=endpoint,
    deployed_model_display_name="clf_model_deployment",
    machine_type="n1-standard-2"
)

print(f'Model deployed to endpoint: {endpoint.resource_name}')