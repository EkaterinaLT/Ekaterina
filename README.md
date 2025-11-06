# Clinical guideline compliance checker

Этот проект предоставляет прототип консольного инструмента, который помогает сопоставлять
клинические рекомендации (PDF или JSON) с картой пациента в формате XML.

## Возможности

* Загрузка клинических рекомендаций из структурированного PDF или JSON.
* Парсинг карты пациента из XML.
* Простая проверка соблюдения: выявление обязательных процедур, которые отсутствуют, и
  противопоказаний, которые были назначены.
* Пример данных в каталоге `examples/`.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Структура входных данных

### Рекомендации

Для JSON ожидается список объектов со следующими полями:

```json
[
  {
    "diagnosis_keywords": ["type", "2", "diabetes"],
    "required_interventions": ["metformin", "lifestyle counseling"],
    "optional_interventions": ["dpp-4 inhibitor"],
    "contraindications": ["sulfonylurea"],
    "notes": "Ensure quarterly HbA1c monitoring."
  }
]
```

Для PDF используется тот же формат, но текст должен быть структурирован блоками вида:

```
Diagnosis: Type 2 diabetes
Required: Metformin; Lifestyle counseling
Optional: DPP-4 inhibitor
Contraindications: Sulfonylurea
Notes: Ensure quarterly HbA1c monitoring.
```

### Карта пациента (XML)

Минимально необходимы следующие элементы:

```xml
<Patient id="123">
  <Identifier>123</Identifier>
  <Diagnosis>Type 2 diabetes</Diagnosis>
  <Treatments>
    <Treatment name="Metformin" />
  </Treatments>
  <Contraindications>
    <Contraindication>None</Contraindication>
  </Contraindications>
</Patient>
```

Инструмент также извлекает дополнительные сведения из `Meta`, если они присутствуют.

## Запуск

```bash
python -m clinical_compliance.cli examples/guidelines.json examples/patient.xml
```

Флаг `--show-all` позволяет вывести информацию по рекомендациям, которые не применимы к
заданному диагнозу.

## Ограничения

* Для корректного анализа PDF необходимо, чтобы документ был структурирован согласно описанному
  формату.
* Это прототип, который не заменяет экспертизу врача. Результаты должны проверяться специалистом.
* Для реальной практики могут потребоваться дополнительные проверки (дозировки, временные рамки,
  взаимодействия препаратов и т. д.).
