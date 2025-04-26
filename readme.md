
# cook-for-kids

A Django application for managing kids' meal planning and scheduling.

## Setup Instructions

### Prerequisites
- Python 3.12
- Git

### Installation

**Clone the repository**
  ```bash
   git clone https://github.com/daberer/cook-for-kids.git
 ```

**Create a virtual environment, install dependencies and set up database**

Create either a conda environment or a Python virtual environment (venv) with Python 3.12.


```Bash
pip install -r requirements.txt
pip install -e .
python manage.py migrate
```

**Create an admin user**

```Bash
python manage.py createsuperuser
```


Follow the prompts to create your admin account.


**Run the development server**




```Bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

MIT License