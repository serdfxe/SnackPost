import subprocess
from pathlib import Path
import shutil
import time

def generate_clients(api_specs_dir: Path, output_dir: Path):
    """
    Генерирует клиенты из OpenAPI спецификаций с помощью openapi-python-client
    
    Args:
        api_specs_dir: Директория с JSON файлами спецификаций (<service-name>-api.json)
        output_dir: Директория для сохранения сгенерированных клиентов
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for spec_file in api_specs_dir.glob("*-api.json"):
        service_name = spec_file.stem.replace("-api", "").replace("-", "_")
        client_dir = output_dir / service_name
        
        print(f"⚙️  Генерация клиента для {service_name} из {spec_file}...")

        if client_dir.exists():
            shutil.rmtree(client_dir)

        try:
            subprocess.run([
                "openapi-python-client",
                "generate",
                "--path",
                str(spec_file),
                "--output-path",
                str(client_dir)
            ], check=True)
            
            time.sleep(2)

            generated_dir = Path(client_dir)
            if generated_dir.exists():
                print(f"✅  Клиент для {service_name} успешно сгенерирован в {client_dir}")
            else:
                print(f"❌  Ошибка: клиент для {service_name} не был сгенерирован")
                
        except subprocess.CalledProcessError as e:
            print(f"❌  Ошибка при генерации клиента для {service_name}: {e}")

def main():
    api_specs_dir = Path("../../../api")
    
    output_dir = Path("./")
    
    generate_clients(api_specs_dir, output_dir)

if __name__ == "__main__":
    main()
