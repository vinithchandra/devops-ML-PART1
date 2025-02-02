# ML-Based CI/CD Quality Gate System

An intelligent CI/CD quality gate system that uses machine learning to predict build outcomes, analyze code quality, and provide automated recommendations for software deployments.

## Features

- Build success prediction using Random Forest Classifier
- Build time estimation using Gradient Boosting Regressor
- Anomaly detection for system metrics
- Git repository analysis and monitoring
- System resource tracking
- Jenkins integration
- Real-time analytics and recommendations

## Project Structure

```
.
├── src/
│   ├── ml/                    # Machine learning models and training
│   ├── collectors/           # Data collection modules
│   ├── analyzers/            # Analysis components
│   ├── integrations/         # External tool integrations
│   └── api/                  # FastAPI web service
├── tests/                    # Test suite
├── config/                   # Configuration files
├── docs/                     # Documentation
└── notebooks/               # Jupyter notebooks for analysis
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

## Usage

1. Start the API server:
```bash
python -m src.api.main
```

2. Run tests:
```bash
pytest tests/
```

3. Check code quality:
```bash
mypy src/
pylint src/
```

## Development

- Follow PEP 8 style guide
- Use type hints
- Write unit tests for new features
- Update documentation as needed

## License

MIT License - see LICENSE file for details
