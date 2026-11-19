# 📖 Hướng Dẫn Kích Hoạt GitHub Profile Đẹp & Hiện Đại

Repo này được thiết kế để làm **GitHub Profile README** đặc biệt cho tài khoản GitHub của bạn (`mtritran`). Khi ai đó truy cập vào trang cá nhân `https://github.com/mtritran`, toàn bộ nội dung của file `README.md` này sẽ được hiển thị trực tiếp với giao diện hiện đại, dynamic badges, thống kê tự động và hiệu ứng con rắn (Snake game).

---

## 🚀 Bước 1: Tạo Repository Trên GitHub

1. Truy cập vào GitHub: [https://github.com/new](https://github.com/new)
2. **Repository name**: Đặt tên **chính xác** là tên username GitHub của bạn: `mtritran`
   - *Lưu ý: GitHub sẽ hiển thị thông báo "You found a secret! ... is a special repository that you can use to add a README.md to your GitHub profile."*
3. **Public / Private**: Chọn **Public** (Bắt buộc phải là Public thì mọi người mới xem được trên profile).
4. **Initialize this repository with**: Không cần tích chọn Add README (vì chúng ta đã tạo sẵn ở local).
5. Bấm nút **Create repository**.

---

## 💻 Bước 2: Push Code Từ Máy Lên GitHub

Mở Terminal (hoặc PowerShell) tại thư mục `D:\Projects\mtritran`:

```bash
cd D:\Projects\mtritran

# Khởi tạo git (nếu chưa có)
git init
git add .
git commit -m "feat: initial modern aesthetic github profile readme"

# Đổi nhánh chính sang main
git branch -M main

# Thêm remote và push (thay URL nếu bạn dùng SSH)
git remote add origin https://github.com/mtritran/mtritran.git
git push -u origin main
```

---

## 🐍 Bước 3: Cấp Quyền Cho GitHub Action (Hiệu Ứng Con Rắn Snake)

Để GitHub Actions tự động cào lịch sử commit và tạo hiệu ứng con rắn ăn đóng góp xanh:

1. Vào repo trên GitHub: `https://github.com/mtritran/mtritran`
2. Chọn tab **Settings** -> **Actions** -> **General**.
3. Cuộn xuống mục **Workflow permissions**:
   - Chọn: **Read and write permissions**.
   - Tích chọn: **Allow GitHub Actions to create and approve pull requests**.
   - Bấm **Save**.
4. Vào tab **Actions** -> Chọn workflow **Generate Snake Animation** ở cột trái -> Bấm nút **Run workflow** -> **Run workflow**.
   - Sau ~1 phút, action sẽ tự động sinh nhánh `output` chứa 2 file ảnh động SVG con rắn cho cả Dark mode và Light mode.

---

## 🎨 Bước 4: Tùy Chỉnh Theo Sở Thích Cá Nhân

Trong file `README.md`:
- **Social Links**: Thay đổi link Gmail, LinkedIn, Facebook của bạn ở phần `<p align="center">...`.
- **Typing SVG**: Tùy chỉnh các dòng chữ chạy tự động ở thẻ `readme-typing-svg`.
- **Tech Stack**: Thêm hoặc bớt icon tại thẻ `skillicons.dev/icons?i=...` (hỗ trợ hàng trăm icon dev: `spring,java,docker,react,vue,angular,golang,c,cpp,aws...`).
- **Quote / Header**: Tùy chọn đổi màu gradient (`customColorList=...`) theo style bạn thích.
