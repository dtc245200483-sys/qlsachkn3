"""Script: Thêm cột tomTat vào bảng Books và điền dữ liệu tóm tắt thực tế."""
import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-P5FMOGL\\QUANGHUNG;'
    'DATABASE=LibraryDB_QA;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes'
)
cursor = conn.cursor()

# 1. Thêm cột tomTat nếu chưa có
cursor.execute("""
    IF NOT EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME='Books' AND COLUMN_NAME='tomTat'
    )
    ALTER TABLE Books ADD tomTat NVARCHAR(MAX) NULL
""")
conn.commit()
print("[OK] Cot tomTat da duoc them (hoac da ton tai)")

# 2. Dữ liệu tóm tắt thực cho từng sách (theo mã sách)
summaries = {
    "5CSKDVKD0002": (
        "Tổng hợp tinh hoa từ 50 tác phẩm kinh điển về kinh doanh và quản trị được đọc nhiều nhất thế giới. "
        "Mỗi cuốn sách được tóm lược thành các ý tưởng cốt lõi, giúp người đọc nắm bắt kiến thức nền tảng "
        "từ những tác giả hàng đầu như Peter Drucker, Philip Kotler, Michael Porter, Dale Carnegie... "
        "Phù hợp cho doanh nhân, sinh viên kinh tế muốn tiếp thu kiến thức đa chiều trong thời gian ngắn."
    ),
    "7TQHQ0003": (
        "Tác phẩm kinh điển của Stephen R. Covey — một trong những cuốn sách phát triển cá nhân bán chạy nhất "
        "mọi thời đại với hơn 40 triệu bản. Covey trình bày 7 thói quen của những người thành công: "
        "Chủ động, Bắt đầu với mục tiêu cuối cùng, Ưu tiên điều quan trọng, Tư duy cùng thắng, "
        "Lắng nghe để hiểu, Tạo sức mạnh cộng hưởng, và Rèn giũa bản thân liên tục. "
        "Cuốn sách thay đổi cách tiếp cận cuộc sống từ từng cá nhân đến tổ chức."
    ),
    "BCA0004": (
        "Parmy Olson — nhà báo của Forbes và The Wall Street Journal — kể lại cuộc cách mạng AI đang diễn ra "
        "với 3 nhân vật trung tâm: Demis Hassabis (DeepMind), Mustafa Suleyman và Sam Altman (OpenAI). "
        "Cuốn sách khám phá cách ChatGPT và các mô hình ngôn ngữ lớn ra đời, cuộc đua giữa các tập đoàn "
        "công nghệ, và những hệ quả đối với xã hội, việc làm và tương lai nhân loại."
    ),
    "BMTM0005": (
        "Kevin Mitnick — từng bị FBI truy nã là hacker nguy hiểm nhất thế giới — kể lại hành trình xâm nhập "
        "vào hệ thống của Motorola, Nokia, Sun Microsystems và nhiều tập đoàn lớn. "
        "Cuốn sách vừa là hồi ký ly kỳ, vừa là bài học thực tiễn về kỹ thuật social engineering — "
        "phương pháp tấn công vào yếu tố con người thay vì máy móc. "
        "Được coi là sách gối đầu giường của cộng đồng an ninh mạng."
    ),
    "BTD0006": (
        "Hồi ký chấn động của Edward Snowden — cựu chuyên viên CIA và NSA — người đã tiết lộ chương trình "
        "giám sát đại trà PRISM của Chính phủ Mỹ vào năm 2013. Snowden kể lại cách anh thu thập bằng chứng, "
        "vượt qua các lớp bảo mật và liên lạc với báo chí quốc tế. Cuốn sách đặt ra câu hỏi sâu sắc về "
        "quyền riêng tư, an ninh quốc gia và trách nhiệm của người nắm giữ bí mật nhà nước."
    ),
    "CCMSVCDTTLTVG0007": (
        "Robert C. Martin (Uncle Bob) trình bày triết lý viết code sạch — code dễ đọc, dễ bảo trì và "
        "dễ mở rộng. Cuốn sách đề cập đến quy tắc đặt tên biến/hàm, cách tổ chức class, viết comment "
        "đúng cách, xử lý lỗi, và unit testing. Đây là tài liệu bắt buộc trong cộng đồng lập trình viên "
        "chuyên nghiệp, giúp phân biệt giữa code chỉ 'chạy được' và code thực sự chất lượng."
    ),
    "CDCNTH0008": (
        "Giáo trình hướng dẫn sử dụng CorelDRAW dành cho người tự học từ cơ bản đến nâng cao. "
        "Bao gồm các kỹ năng vẽ vector, thiết kế logo, banner, name card và bố cục ấn phẩm. "
        "Phù hợp cho sinh viên ngành thiết kế đồ họa, nhân viên marketing hoặc bất kỳ ai muốn "
        "làm chủ phần mềm thiết kế đồ họa phổ biến này."
    ),
    "CNKT0009": (
        "Giáo trình chuyên ngành kỹ thuật điện tử chuẩn quốc tế, bao gồm lý thuyết về mạch điện, "
        "linh kiện điện tử, hệ thống nhúng và viễn thông. Cung cấp nền tảng kỹ thuật vững chắc "
        "cho sinh viên ngành Điện tử - Viễn thông, phù hợp với chương trình đào tạo đại học kỹ thuật."
    ),
    "CSDLMXS0010": (
        "Giáo trình chuyên ngành cung cấp nền tảng toán học cho khoa học dữ liệu và thống kê ứng dụng. "
        "Bao gồm lý thuyết xác suất, phân phối thống kê, kiểm định giả thuyết và ứng dụng trong "
        "phân tích dữ liệu thực tế. Phù hợp cho sinh viên công nghệ thông tin, khoa học dữ liệu và toán ứng dụng."
    ),
    "CSSCOTTCBDNC0011": (
        "Bộ 2 cuốn sách chuyên sâu về kỹ thuật sửa chữa ô tô: cuốn cơ bản hướng dẫn từ cấu tạo động cơ, "
        "hệ thống điện, phanh, lái; cuốn nâng cao đi sâu vào chẩn đoán lỗi hiện đại, hệ thống OBD, "
        "điện tử ô tô và công nghệ hybrid. Bộ sách lý tưởng cho học viên sửa chữa ô tô và thợ bậc cao."
    ),
    "DDTD0012": (
        "Câu chuyện của những kỹ sư Việt Nam làm việc tại BMW và Bosch ở Đức, rồi trở về đóng góp cho "
        "dự án ô tô điện VinFast. Cuốn sách ghi lại hành trình chuyển giao công nghệ, thách thức kỹ thuật "
        "và khát vọng xây dựng thương hiệu ô tô Việt Nam đủ sức cạnh tranh quốc tế."
    ),
    "DTTC0013": (
        "Giới thiệu các nguyên tắc và phương pháp đầu tư tài chính cơ bản: phân tích cổ phiếu, trái phiếu, "
        "quỹ đầu tư, bất động sản và các công cụ tài chính phái sinh. Cuốn sách giúp nhà đầu tư cá nhân "
        "xây dựng danh mục đầu tư đa dạng và quản lý rủi ro hiệu quả trong thị trường Việt Nam."
    ),
    "GDM0014": (
        "Clifford Stoll — nhà thiên văn học kiêm quản trị hệ thống tại Đại học Berkeley — kể lại câu chuyện "
        "có thật về việc phát hiện và truy theo nhóm hacker Đức xâm nhập vào các máy tính của Chính phủ Mỹ "
        "năm 1986-1987. Đây là một trong những vụ điều tra tội phạm mạng đầu tiên trong lịch sử, "
        "được kể lại với văn phong hấp dẫn như tiểu thuyết trinh thám."
    ),
    "GTCH0015": (
        "Giáo trình chính thức do Hanban (Hội đồng Hán ngữ Quốc tế) biên soạn để luyện thi chứng chỉ "
        "HSK (Hán ngữ Thủy bình Khảo thí) — chứng chỉ tiếng Trung phổ thông được công nhận toàn cầu. "
        "Cấp độ sơ cấp bao gồm 150 từ vựng cơ bản, các mẫu câu giao tiếp thông dụng và bài tập luyện thi."
    ),
    "GTCSATTT0016": (
        "Giáo trình đại học hệ thống về an toàn thông tin: mã hóa dữ liệu, xác thực người dùng, "
        "bảo mật mạng, tường lửa, phát hiện xâm nhập và an toàn ứng dụng web. "
        "Được thiết kế cho sinh viên ngành Công nghệ thông tin và An toàn thông tin, "
        "cung cấp cả lý thuyết nền tảng lẫn thực hành kỹ năng bảo mật."
    ),
    "GTCXXXV20017": (
        "Giáo trình toàn diện về CorelDRAW từ phiên bản X7 đến 2020, cập nhật các tính năng mới nhất. "
        "Hướng dẫn từ giao diện cơ bản, công cụ vẽ vector, thiết kế logo, bố cục trang in ấn, "
        "đến xuất file đa định dạng. Phù hợp cho sinh viên và người đi làm trong lĩnh vực đồ họa."
    ),
    "GTDCDT0018": (
        "Giáo trình đại học về động cơ đốt trong — trái tim của mọi phương tiện cơ giới. "
        "Trình bày nguyên lý nhiệt động học, chu trình làm việc của động cơ xăng và diesel, "
        "hệ thống cung cấp nhiên liệu, làm mát, bôi trơn và khởi động. "
        "Tài liệu chuẩn cho sinh viên ngành Kỹ thuật Ô tô và Cơ khí Động lực."
    ),
    "GTHN0019": (
        "Giáo trình Hán ngữ quyển 1 — tập thượng dành cho người mới bắt đầu học tiếng Trung. "
        "Bao gồm 15 bài học với chủ đề giao tiếp thông dụng: chào hỏi, gia đình, mua sắm, đi lại. "
        "Mỗi bài có từ vựng mới, ngữ pháp giải thích rõ ràng và bài tập thực hành đa dạng."
    ),
    "GTPTHN0020": (
        "Giáo trình phát triển kỹ năng nói và giao tiếp tiếng Trung cấp trung cấp 1. "
        "Tập trung vào luyện nói thông qua các tình huống thực tế: phỏng vấn xin việc, họp hành, "
        "thuyết trình và giao tiếp xã hội. Kèm theo bài tập nghe và ghi chú từ âm thanh thực tế."
    ),
    "GTVDKA0021": (
        "Giáo trình chuyên sâu về lập trình vi điều khiển ARM — dòng vi xử lý phổ biến nhất trên "
        "thế giới hiện nay. Hướng dẫn chi tiết lập trình STM32 với HAL Library, GPIO, Timer, UART, "
        "SPI, I2C và interrupt. Phù hợp cho sinh viên điện tử, kỹ sư hệ thống nhúng."
    ),
    "HDCBMVQTMCNTH0022": (
        "Sách kỹ thuật trong nước hướng dẫn toàn diện về bảo mật và quản trị mạng máy tính dành cho "
        "người tự học. Bao gồm cài đặt tường lửa, VPN, quản trị Active Directory, giám sát mạng, "
        "phát hiện xâm nhập và xử lý sự cố bảo mật. Phù hợp cho quản trị viên hệ thống và kỹ thuật viên mạng."
    ),
    "HLS0023": (
        "Steven Levy kể lại lịch sử huyền thoại của phong trào hacker từ những năm 1950 tại MIT "
        "đến sự ra đời của máy tính cá nhân và phần mềm nguồn mở. Cuốn sách giới thiệu các tên tuổi "
        "huyền thoại như Richard Stallman, Bill Gates thời trẻ, và những người đặt nền móng cho "
        "văn hóa hacker — thứ đã định hình thế giới công nghệ ngày nay."
    ),
    "HTAGTCT3N0024": (
        "Giáo trình thực hành tiếng Anh giao tiếp được thiết kế để người học có thể tự học trong 30 ngày. "
        "Bao gồm các chủ đề giao tiếp hàng ngày: giới thiệu bản thân, hỏi đường, đặt phòng khách sạn, "
        "gọi món ở nhà hàng, mua sắm. Kèm CD phát âm chuẩn theo giọng bản ngữ."
    ),
    "HTTTTCNH0025": (
        "Giáo trình chuyên ngành về hệ thống thông tin tài chính ngân hàng: cơ sở dữ liệu tài chính, "
        "hệ thống core banking, quản lý rủi ro IT, bảo mật giao dịch điện tử và fintech. "
        "Phù hợp cho sinh viên ngành Tài chính - Ngân hàng và Công nghệ thông tin ứng dụng trong lĩnh vực tài chính."
    ),
    "KTA0026": (
        "Sách kỹ thuật AI thực hành hướng dẫn xây dựng ứng dụng thông minh sử dụng các mô hình ngôn ngữ lớn (LLM). "
        "Bao gồm: tích hợp API của OpenAI/Gemini, xây dựng chatbot, RAG (Retrieval-Augmented Generation), "
        "prompt engineering và triển khai ứng dụng AI trong môi trường thực tế."
    ),
    "KTBDVSCOTHD0027": (
        "Sách kỹ thuật chuyên sâu về bảo dưỡng ô tô hiện đại: quy trình kiểm tra định kỳ, thay thế "
        "dầu nhớt, phanh, lọc gió, bugi và các chi tiết quan trọng. Hướng dẫn đọc cẩm nang xe, "
        "sử dụng thiết bị đo lường và chẩn đoán lỗi theo tiêu chuẩn nhà sản xuất."
    ),
    "KTBDVSCOTHD0028": (
        "Tập trung vào hệ thống điện ô tô hiện đại: sơ đồ mạch điện thân xe, hệ thống điều khiển động cơ ECU, "
        "ABS/ESP, túi khí, hệ thống thông tin giải trí và các cảm biến. Hướng dẫn đọc mã lỗi OBD-II "
        "và sửa chữa các mạch điện phổ biến trên xe hơi thế hệ mới."
    ),
    "KTLTPNC0029": (
        "Dành cho người đã có nền tảng Python cơ bản, cuốn sách đi sâu vào các kỹ thuật nâng cao: "
        "lập trình hướng đối tượng, decorator, generator, xử lý đa luồng/đa tiến trình, "
        "làm việc với API, xử lý dữ liệu lớn với Pandas và NumPy. "
        "Phù hợp cho lập trình viên Python muốn nâng cao kỹ năng lên mức chuyên nghiệp."
    ),
    "KTSCOTCB0030": (
        "Giáo trình cơ bản và đầy đủ về sửa chữa ô tô, bao gồm toàn bộ các hệ thống: "
        "động cơ, hệ thống lái, phanh, truyền động, điều hòa không khí và thân vỏ xe. "
        "Tái bản 2019 cập nhật thêm nội dung về hệ thống điện tử và chuẩn đoán hiện đại. "
        "Đây là tài liệu tham khảo tiêu chuẩn trong các trường dạy nghề sửa chữa ô tô."
    ),
    "KTSCOTNC0031": (
        "Giáo trình nâng cao về sửa chữa ô tô dành cho thợ bậc cao và kỹ sư bảo dưỡng. "
        "Đi sâu vào các hệ thống phức tạp: hộp số tự động, hệ thống phanh ABS/EBD, "
        "hệ thống treo thông minh, điều khiển hành trình và công nghệ hybrid/điện. "
        "Yêu cầu người đọc đã có kiến thức cơ bản về ô tô."
    ),
    "LTCB0032": (
        "Cuốn sách dạy lập trình Python từ zero bằng phương pháp trực quan với hình ảnh minh họa. "
        "Không cần nền tảng lập trình trước, người đọc sẽ học qua các bài toán thực tế: "
        "tính toán, xử lý chuỗi, làm việc với file, và xây dựng ứng dụng nhỏ đầu tiên. "
        "Phù hợp cho học sinh, sinh viên và người chuyển ngành sang lập trình."
    ),
    "LTDKTACHVVKN0033": (
        "Hướng dẫn xây dựng hệ thống IoT (Internet of Things) với Arduino làm trung tâm điều khiển. "
        "Kết nối cảm biến nhiệt độ, độ ẩm, ánh sáng với internet, gửi dữ liệu lên cloud, "
        "điều khiển thiết bị từ xa qua smartphone. Thực hành với các module WiFi (ESP8266), "
        "MQTT protocol và dashboard giám sát thời gian thực."
    ),
    "LTDKVA0034": (
        "Giới thiệu toàn diện về lập trình Arduino — nền tảng phần cứng mã nguồn mở phổ biến nhất "
        "thế giới cho các dự án điện tử DIY và giáo dục STEM. Bao gồm: lập trình C/C++ cho Arduino, "
        "điều khiển LED, motor, servo, đọc cảm biến, giao tiếp LCD và xây dựng robot đơn giản."
    ),
    "LTVP0035": (
        "Sách lập trình Python hướng đến thế hệ sinh viên và người mới bắt đầu, "
        "đặt Python trong bối cảnh ứng dụng thực tế của tương lai: AI, data science, automation. "
        "Nội dung bao gồm cú pháp cơ bản, cấu trúc dữ liệu, hàm, module và các thư viện phổ biến. "
        "Phù hợp như hành trang kỹ năng số cho sinh viên mọi ngành."
    ),
    "LTVVDKP0036": (
        "Giáo trình đại học kết hợp lý thuyết và thực hành lập trình vi điều khiển PIC — "
        "một trong những dòng vi điều khiển phổ biến nhất trong công nghiệp. "
        "Bao gồm kiến trúc PIC, lập trình C với MPLAB, các module ngoại vi: ADC, PWM, Timer, UART, "
        "SPI và thiết kế mạch thực tế. Kèm bài thực hành có sơ đồ mạch."
    ),
    "LVQTCCU0037": (
        "Giáo trình toàn diện về Logistics và Quản trị chuỗi cung ứng — lĩnh vực then chốt trong "
        "thương mại toàn cầu. Bao gồm: quản lý kho bãi, vận tải đa phương thức, quản lý nhà cung cấp, "
        "dự báo nhu cầu, tối ưu tồn kho và ứng dụng công nghệ trong SCM hiện đại. "
        "Phù hợp cho sinh viên kinh tế, thương mại và nhà quản lý chuỗi cung ứng."
    ),
    "MBLDK0038": (
        "Khám phá chiến lược Marketing bán lẻ trong thời đại đa kênh (Omnichannel): "
        "kết hợp cửa hàng vật lý với thương mại điện tử, mạng xã hội và ứng dụng di động. "
        "Phân tích hành vi người tiêu dùng đa kênh, chiến lược giá, trải nghiệm khách hàng "
        "và đo lường hiệu quả marketing trên các nền tảng Shopee, Lazada, TikTok Shop."
    ),
    "MCB0039": (
        "Giáo trình Marketing căn bản — Marketing 101 — cung cấp nền tảng lý thuyết marketing "
        "theo chuẩn quốc tế: 4P (Product, Price, Place, Promotion), phân tích thị trường, "
        "phân khúc khách hàng, định vị thương hiệu và xây dựng chiến lược marketing tích hợp. "
        "Phù hợp cho sinh viên và người mới bắt đầu trong lĩnh vực marketing."
    ),
    "MHPPVBL0040": (
        "Phân tích các mô hình phân phối và bán lẻ hiện đại tại Việt Nam và trên thế giới: "
        "siêu thị, đại lý, nhượng quyền thương mại (franchise), direct-to-consumer và dropshipping. "
        "Đánh giá ưu nhược điểm từng mô hình và hướng dẫn lựa chọn kênh phân phối phù hợp "
        "với quy mô và ngành hàng của doanh nghiệp."
    ),
    "NDTTM0041": (
        "Bản dịch tiếng Việt của 'The Intelligent Investor' — kiệt tác đầu tư giá trị của Benjamin Graham, "
        "người thầy của Warren Buffett. Graham trình bày triết lý đầu tư dài hạn dựa trên phân tích "
        "cơ bản, biên độ an toàn (margin of safety) và tâm lý thị trường. "
        "Warren Buffett gọi đây là 'cuốn sách đầu tư hay nhất từng được viết'."
    ),
    "NGCNTB0042": (
        "George S. Clason kể các câu chuyện ngụ ngôn đặt trong thành phố Babylon cổ đại, "
        "truyền đạt 7 bí quyết làm giàu vượt thời gian: tiết kiệm ít nhất 1/10 thu nhập, "
        "đầu tư khôn ngoan, tránh nợ xấu, bảo vệ tài sản và tăng thu nhập chủ động. "
        "Được xuất bản lần đầu năm 1926, đây là một trong những cuốn sách tài chính cá nhân "
        "được yêu thích và đọc nhiều nhất mọi thời đại."
    ),
    "NLDTG0043": (
        "Sách nghệ thuật bìa cứng khổ lớn trình bày các nguyên lý thiết kế thị giác căn bản: "
        "bố cục (layout), màu sắc, typography (chữ), hình ảnh và khoảng trắng. "
        "Với hơn 300 ví dụ trực quan, cuốn sách giúp người học phát triển con mắt thẩm mỹ "
        "và tư duy thiết kế chuyên nghiệp. Dành cho sinh viên và nhà thiết kế muốn nâng cao trình độ."
    ),
    "NLM0044": (
        "Giáo trình Nguyên lý Marketing toàn diện cho sinh viên đại học và cao học: "
        "lý thuyết marketing hiện đại, nghiên cứu thị trường, hành vi người tiêu dùng, "
        "chiến lược sản phẩm, giá, phân phối và truyền thông marketing. "
        "Kết hợp lý thuyết với case study từ doanh nghiệp Việt Nam và quốc tế."
    ),
    "NMCSDL0045": (
        "Giáo trình Nhập môn Cơ sở dữ liệu của Đại học Bách Khoa Hà Nội, dùng trong chương trình "
        "đào tạo kỹ sư CNTT. Bao gồm: mô hình thực thể - quan hệ (ER), thiết kế lược đồ quan hệ, "
        "chuẩn hóa (normalization), SQL cơ bản và nâng cao, giao dịch và phục hồi dữ liệu."
    ),
    "NTAM0046": (
        "Kevin Mitnick và Robert Vamosi hướng dẫn cách bảo vệ sự riêng tư trong thế giới kỹ thuật số: "
        "ẩn danh trên internet, mã hóa thông tin liên lạc, bảo vệ điện thoại, laptop, "
        "tránh bị theo dõi qua metadata và sử dụng các công cụ như Tor, VPN, Signal. "
        "Viết cho đại chúng nhưng đủ kỹ thuật để áp dụng thực tế."
    ),
    "TAGTTPN0047": (
        "Giáo trình tiếng Anh chuyên ngành dành riêng cho nhân viên và sinh viên ngành Nha khoa. "
        "Bao gồm từ vựng chuyên môn về răng miệng, các mẫu câu giao tiếp với bệnh nhân nước ngoài, "
        "giải thích thủ thuật, tư vấn điều trị và giao tiếp với đối tác quốc tế trong lĩnh vực nha khoa."
    ),
    "TCCB0048": (
        "Frank Fabozzi và Pamela Drake trình bày kiến thức tài chính toàn diện từ căn bản: "
        "giá trị thời gian của tiền, định giá cổ phiếu và trái phiếu, quản trị rủi ro tài chính, "
        "cấu trúc vốn doanh nghiệp và các công cụ tài chính phái sinh. "
        "Phù hợp cho sinh viên tài chính, kế toán và nhà quản trị tài chính doanh nghiệp."
    ),
    "TGTHN0049": (
        "Tân Giáo trình Hán ngữ Tập 1 — giáo trình học tiếng Trung được biên soạn theo phương pháp "
        "giao tiếp hiện đại, dùng phổ biến tại các trường đại học Việt Nam. "
        "Bao gồm phát âm (pinyin), 600 từ vựng cơ bản và 30 bài học tình huống thực tế "
        "trong cuộc sống, học tập và công việc."
    ),
    "TH2CDGTTATDN0050": (
        "Giáo trình tự học tiếng Anh giao tiếp với 29 chủ đề thông dụng nhất trong cuộc sống: "
        "giới thiệu bản thân, sở thích, gia đình, công việc, du lịch, sức khỏe, ăn uống và mua sắm. "
        "Mỗi chủ đề có bảng từ vựng, hội thoại mẫu và bài tập kiểm tra. "
        "Phù hợp cho người đi làm muốn tự cải thiện tiếng Anh giao tiếp."
    ),
    "THAICBHMH0051": (
        "Hướng dẫn tự học Adobe InDesign CS5 — phần mềm dàn trang chuyên nghiệp của Adobe — "
        "thông qua hình ảnh minh họa từng bước. Bao gồm thiết kế sách, tạp chí, brochure, catalogue "
        "và xuất file in ấn chuẩn chất lượng. Phù hợp cho sinh viên và nhà thiết kế in ấn."
    ),
    "THGTTATCD0052": (
        "Giáo trình dạy tiếng Anh giao tiếp theo từng chủ đề cụ thể: ở công sở, tại bệnh viện, "
        "trong cuộc họp quốc tế, khi đi phỏng vấn xin việc. Mỗi chủ đề có từ vựng chuyên biệt, "
        "đoạn hội thoại mẫu và ghi chú về văn hóa giao tiếp. Giúp người học dùng tiếng Anh "
        "tự tin trong từng bối cảnh cụ thể của cuộc sống."
    ),
    "THICTTKDH0053": (
        "Hướng dẫn tự học Adobe Illustrator CS6 — công cụ thiết kế vector hàng đầu — "
        "ứng dụng trong thiết kế đồ họa chuyên nghiệp. Bao gồm thiết kế logo, poster, icon, "
        "infographic và minh họa kỹ thuật số. Giải thích chi tiết các công cụ Pen, Pathfinder, "
        "Gradient và hiệu ứng vector nâng cao."
    ),
    "THPBHA0054": (
        "Hướng dẫn tự học Proteus — phần mềm mô phỏng mạch điện tử phổ biến trong giáo dục kỹ thuật — "
        "bằng hình ảnh trực quan. Bao gồm vẽ sơ đồ nguyên lý, mô phỏng mạch số và tương tự, "
        "lập trình vi điều khiển ảo và thiết kế PCB. Phù hợp cho sinh viên điện tử và kỹ thuật điện."
    ),
    "THPCTT0055": (
        "Giáo trình học Photoshop CC toàn tập — từ các công cụ cơ bản đến kỹ thuật nâng cao. "
        "Tái bản 2023 cập nhật các tính năng AI mới như Generative Fill và Neural Filters. "
        "Bao gồm: chỉnh sửa ảnh chuyên nghiệp, ghép ảnh, retouching, thiết kế web, "
        "và tạo hiệu ứng đặc biệt. Phù hợp cho nhiếp ảnh viên và nhà thiết kế đồ họa."
    ),
    "THQTCCU0056": (
        "Tổng hợp tinh hoa kiến thức về quản trị chuỗi cung ứng từ lý thuyết đến thực tiễn. "
        "Phân tích các chiến lược chuỗi cung ứng của Apple, Toyota, Amazon và các công ty toàn cầu. "
        "Bao gồm: tối ưu hóa quy trình, quản lý rủi ro chuỗi cung ứng và ứng dụng "
        "công nghệ blockchain, AI trong SCM hiện đại."
    ),
    "TIITDBOVI0057": (
        "The Intelligent Investor in its original English edition by Benjamin Graham — "
        "the definitive book on value investing updated with commentary by Jason Zweig. "
        "Graham introduces concepts of 'Mr. Market', margin of safety, and the distinction "
        "between investing and speculation. Warren Buffett called it 'the best book about investing "
        "ever written' and credits it as the foundation of his investment philosophy."
    ),
    "TKDHVIC0058": (
        "Hướng dẫn toàn diện về thiết kế đồ họa với Adobe Illustrator CS4: "
        "từ làm quen giao diện, sử dụng các công cụ vẽ cơ bản đến thiết kế đồ họa phức tạp. "
        "Thực hành thiết kế logo chuyên nghiệp, bộ nhận diện thương hiệu, bìa sách, "
        "poster sự kiện và các ấn phẩm in ấn chất lượng cao."
    ),
    "TSNNT0059": (
        "Bộ sách chuyên ngành kỹ thuật ô tô và xe máy hiện đại từ thư viện 'Nhất nghề tinh'. "
        "Bao gồm kỹ thuật sửa chữa, bảo dưỡng các hệ thống cơ khí, điện và điện tử trên "
        "ô tô và xe máy thế hệ mới. Cung cấp kiến thức chuyên sâu theo từng hệ thống "
        "với hình ảnh kỹ thuật rõ ràng và quy trình thực hành chi tiết."
    ),
    "TTNHVTTTC0060": (
        "Giáo trình về Tiền tệ - Ngân hàng và Thị trường Tài chính theo chương trình đào tạo "
        "chuẩn quốc tế. Bao gồm: bản chất và chức năng của tiền, hệ thống ngân hàng thương mại, "
        "Ngân hàng Trung ương và chính sách tiền tệ, thị trường vốn, thị trường chứng khoán "
        "và thị trường ngoại hối. Phù hợp cho sinh viên ngành Tài chính - Ngân hàng - Kinh tế."
    ),
    "TTTC0061": (
        "Karen Berman, Joe Knight và John Case giải thích các khái niệm tài chính phức tạp "
        "bằng ngôn ngữ dễ hiểu cho người không chuyên về tài chính. "
        "Bao gồm: đọc hiểu báo cáo tài chính (Bảng cân đối kế toán, Báo cáo lãi lỗ, Dòng tiền), "
        "đánh giá sức khỏe tài chính doanh nghiệp và ra quyết định kinh doanh dựa trên số liệu."
    ),
    "UDVXLVVDK0062": (
        "Sách kỹ thuật về ứng dụng vi xử lý và vi điều khiển trong các hệ thống điều khiển công nghiệp. "
        "Bao gồm kiến trúc vi xử lý, giao tiếp ngoại vi, lập trình assembly và C nhúng, "
        "ứng dụng trong điều khiển động cơ, thu thập dữ liệu và hệ thống nhúng thời gian thực. "
        "Phù hợp cho kỹ sư điện tử và sinh viên chuyên ngành kỹ thuật điện tử."
    ),
    "VDKVUD0063": (
        "Hướng dẫn vi điều khiển Arduino cho người tự học từ số không: từ cài đặt môi trường lập trình, "
        "lập trình LED nhấp nháy đầu tiên đến các dự án thực tế như đồng hồ kỹ thuật số, "
        "trạm thời tiết và robot tự động. Lý giải rõ ràng từng dòng code, "
        "phù hợp tuyệt đối cho người không có nền tảng điện tử trước đó."
    ),
    "VKHH0064": (
        "David E. Sanger — nhà báo New York Times — tiết lộ các chiến dịch tấn công mạng bí mật "
        "của Mỹ, Israel, Nga, Trung Quốc và Triều Tiên: từ virus Stuxnet phá hoại chương trình hạt nhân Iran, "
        "tấn công lưới điện Ukraine, đến can thiệp bầu cử Mỹ 2016. "
        "Cuốn sách vẽ ra bức tranh toàn cảnh về chiến tranh mạng — mặt trận vô hình định hình địa chính trị thế kỷ 21."
    ),
}

print(f"[INFO] Se cap nhat {len(summaries)} ban ghi tomTat...")

for ma, tom_tat in summaries.items():
    cursor.execute(
        "UPDATE Books SET tomTat = ? WHERE ma = ?",
        (tom_tat, ma)
    )

conn.commit()
print(f"[OK] Da cap nhat {len(summaries)} ban ghi tomTat thanh cong!")

# Verify
cursor.execute("SELECT COUNT(*) FROM Books WHERE tomTat IS NOT NULL")
count = cursor.fetchone()[0]
print(f"[CHECK] So sach co tomTat: {count}")

conn.close()
