from core.snippets_manager import SnippetsManager

manager = SnippetsManager()

# agregar snippet de prueba
snippet = manager.add(
    group="Test",
    title="Prueba",
    content="Esto es un snippet de prueba"
)

print("Snippet creado:", snippet)

# listar todos
print("Todos los snippets:")
for s in manager.get_all():
    print(s["title"])