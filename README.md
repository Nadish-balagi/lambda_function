# Lambda: S3 → Postgres RDS Data Loader

This project uploads CSV data from an **Amazon S3 bucket** to a **PostgreSQL database hosted on Amazon RDS** using an **AWS Lambda function** packaged as a Docker image.

---

## 🚀 Features
- **Triggered by S3** – Automatically runs when a new CSV file is uploaded.
- **Data Cleaning** – Cleans column names (lowercased & spaces replaced with underscores).
- **Bulk Upload** – Inserts thousands of rows efficiently into a Postgres table using Pandas + SQLAlchemy.
- **Docker-based Lambda** – Packaged in a container for easy deployment.

---

## 📂 Project Structure
lambda_pandas_new/
├── app.py # Main Lambda handler
├── Dockerfile # Dockerfile for AWS Lambda
├── requirements.txt # Python dependencies
└── README.md # Project documentation

yaml
Copy
Edit

---

## ⚙️ Technologies Used
- **AWS Lambda** (Python 3.12, Docker container)
- **AWS S3** (CSV storage)
- **AWS RDS (Postgres)** (Target database)
- **Pandas & SQLAlchemy** (Data processing & upload)
- **Boto3** (S3 interaction)

---

## 🔧 Setup & Deployment

### **1. Build & Push Docker Image to ECR**
```bash
# Authenticate to AWS ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com

# Build Docker image
docker build -t lambda-pandas-new .

# Tag image for ECR
docker tag lambda-pandas-new:latest <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/lambda-pandas-new:latest

# Push to ECR
docker push <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/lambda-pandas-new:latest
2. Update Lambda Function
bash
Copy
Edit
aws lambda update-function-code \
    --function-name lambda-pandas-fn \
    --image-uri <ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com/lambda-pandas-new:latest
Set these environment variables in Lambda:

Variable	Value
PG_HOST	your-rds-endpoint (e.g., ticket-booking-db.cjyseogkuhaa.ap-south-1.rds.amazonaws.com)
PG_PORT	5432
PG_DATABASE	postgres
PG_USER	postgres
PG_PASSWORD	your-password
PG_TABLE	ticket_booking_sample

3. Triggering
Automatic Trigger: Configure an S3 event notification to invoke Lambda on CSV upload.

Manual Test: Use the Lambda Test console with a sample event:

json
Copy
Edit
{
  "Records": [
    {
      "s3": {
        "bucket": { "name": "your-bucket-name" },
        "object": { "key": "customer_booking.csv" }
      }
    }
  ]
}
✅ Expected Logs
Successful Execution:

pgsql
Copy
Edit
📥 Downloading: s3://your-bucket/customer_booking.csv → /tmp/customer_booking.csv
✅ Cleaned columns: ['num_passengers', 'sales_channel', '...']
✅ Uploaded 50000 rows to ticket_booking_sample
Common Error (before RDS fix):

vbnet
Copy
Edit
❌ Error: (psycopg2.OperationalError) connection to server ... failed: Connection timed out
🖥️ Connect to RDS (Optional)
You can verify data using pgAdmin or psql:

sql
Copy
Edit
SELECT COUNT(*) FROM public.ticket_booking_sample;
