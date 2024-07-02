package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"strings"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/ledongthuc/pdf"
)

var (
	db       *pgxpool.Pool
	s3Client *s3.S3
)

func init() {
	// Initialize S3 client
	sess := session.Must(session.NewSession(&aws.Config{
		Region: aws.String(os.Getenv("AWS_REGION")),
	}))
	s3Client = s3.New(sess)

	// Initialize PostgreSQL connection
	dbURL := fmt.Sprintf("postgres://%s:%s@%s:%s/%s",
		os.Getenv("DB_USER"),
		os.Getenv("DB_PASSWORD"),
		os.Getenv("DB_HOST"),
		os.Getenv("DB_PORT"),
		os.Getenv("DB_NAME"),
	)
	var err error
	db, err = pgxpool.Connect(context.Background(), dbURL)
	if err != nil {
		log.Fatalf("Unable to connect to database: %v\n", err)
	}
}

func handler(ctx context.Context, s3Event events.S3Event) error {
	for _, record := range s3Event.Records {
		s3Record := record.S3
		bucket := s3Record.Bucket.Name
		key := s3Record.Object.Key

		// Get the object from S3
		resp, err := s3Client.GetObject(&s3.GetObjectInput{
			Bucket: aws.String(bucket),
			Key:    aws.String(key),
		})
		if err != nil {
			return fmt.Errorf("failed to get object %s from bucket %s, %v", key, bucket, err)
		}

		// Read the object content
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return fmt.Errorf("failed to read object body: %v", err)
		}

		// Determine the file type and extract content accordingly
		var content string
		if strings.HasSuffix(key, ".txt") {
			content = string(body)
		} else if strings.HasSuffix(key, ".pdf") {
			content, err = extractTextFromPDF(body)
			if err != nil {
				return fmt.Errorf("failed to extract text from PDF: %v", err)
			}
		} else {
			log.Printf("Unsupported file type: %s", key)
			continue
		}

		// Insert the document into the database
		_, err = db.Exec(ctx, "INSERT INTO documents (filename, content, object_key) VALUES ($1, $2, $3)", key, content, key)
		if err != nil {
			return fmt.Errorf("failed to insert document into database: %v", err)
		}
	}
	return nil
}

func extractTextFromPDF(fileContent []byte) (string, error) {
	r, err := pdf.NewReader(strings.NewReader(string(fileContent)), int64(len(fileContent)))
	if err != nil {
		return "", err
	}
	totalPage := r.NumPage()
	var textBuilder strings.Builder
	for pageIndex := 1; pageIndex <= totalPage; pageIndex++ {
		page := r.Page(pageIndex)
		if page.V.IsNull() {
			continue
		}
		text, err := page.GetPlainText(nil)
		if err != nil {
			return "", err
		}
		textBuilder.WriteString(text)
	}
	return textBuilder.String(), nil
}

func main() {
	lambda.Start(handler)
}
