FROM public.ecr.aws/lambda/python:3.12

# ✅ Use dnf for Amazon Linux 2023
RUN dnf install -y postgresql-devel gcc python3-devel && dnf clean all

# ✅ Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt -t ${LAMBDA_TASK_ROOT}

# ✅ Copy Lambda function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# ✅ Lambda function handler
CMD ["lambda_function.lambda_handler"]
