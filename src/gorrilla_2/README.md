# Gorilla Large Action Model POC

Đây là một Proof of Concept (POC) triển khai Gorilla Large Action Model. Gorilla là một mô hình ngôn ngữ lớn được thiết kế đặc biệt để hiểu và thực thi các hành động phức tạp từ ngôn ngữ tự nhiên.

## Giới thiệu về Gorilla

Gorilla là một Large Action Model (LAM) được phát triển bởi UC Berkeley. Nó có khả năng:
- Hiểu và thực thi các hành động từ ngôn ngữ tự nhiên
- Tích hợp với các API và dịch vụ bên ngoài
- Học và thích nghi với các hành động mới
- Xử lý các tác vụ phức tạp một cách tự động

## Tính năng

- Tích hợp mô hình Gorilla-7B
- Hỗ trợ các hành động:
  - Đọc file
  - Gửi HTTP requests
- API RESTful với FastAPI
- Tích hợp với Azure OpenAI (tùy chọn)

## Cài đặt

1. Tạo môi trường ảo:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc
.venv\Scripts\activate  # Windows
```

2. Cài đặt các thư viện:
```bash
pip install -r requirements.txt
```

3. Cấu hình biến môi trường:
- Sao chép file `.env.example` thành `.env`
- Cập nhật các giá trị trong `.env` với thông tin Azure OpenAI của bạn (nếu sử dụng)

## Chạy ứng dụng

```bash
uvicorn main:app --reload
```

## API Endpoints

### 1. Chat
```
POST /chat
Content-Type: application/json

{
    "message": "your natural language query here"
}
```

### 2. List Actions
```
GET /actions
```

## Ví dụ sử dụng

1. Đọc file:
```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{
    "message": "read the contents of config.json"
}'
```

2. Gửi HTTP request:
```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{
    "message": "get data from https://api.example.com"
}'
```

## Cấu trúc Code

- `main.py`: File chính chứa triển khai Gorilla
- `requirements.txt`: Danh sách các thư viện cần thiết
- `.env`: Cấu hình biến môi trường

## Các Class Chính

1. `Action`: Mô hình cho một hành động có thể thực thi
2. `ActionRegistry`: Quản lý đăng ký và truy xuất các hành động
3. `Gorilla`: Class chính xử lý các truy vấn và thực thi hành động

## Bảo mật

- Kiểm tra quyền truy cập cho mỗi hành động
- Xác thực API key cho Azure OpenAI (nếu sử dụng)
- Xử lý lỗi và ngoại lệ

## Mở rộng

Bạn có thể thêm các hành động mới bằng cách:
1. Tạo một instance mới của `Action`
2. Đăng ký nó với `ActionRegistry`
3. Thêm logic xử lý trong `Gorilla._execute_action()`

## Tài liệu Tham khảo

- [Gorilla Official Website](https://gorilla.cs.berkeley.edu/)
- [Gorilla GitHub Repository](https://github.com/ShishirPatil/gorilla)
- [Gorilla Paper](https://arxiv.org/abs/2305.15334) 