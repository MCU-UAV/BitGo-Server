#### 1. 用户表 (users)

| 列名            | 数据类型     | 约束                        |
| --------------- | ------------ | --------------------------- |
| id              | INT          | AUTO_INCREMENT, PRIMARY KEY |
| username        | VARCHAR(255) | UNIQUE, NOT NULL            |
| hashed_password | VARCHAR(255) | NOT NULL                    |
| email           | VARCHAR(255) | UNIQUE, NOT NULL            |
| created_at      | DATETIME     | DEFAULT CURRENT_TIMESTAMP   |

#### 2. 产品表 (products)

| 列名        | 数据类型       | 约束                                   |
| ----------- | -------------- | -------------------------------------- |
| id          | INT            | AUTO_INCREMENT, PRIMARY KEY            |
| name        | VARCHAR(255)   | NOT NULL                               |
| description | TEXT           |                                        |
| price       | DECIMAL(10, 2) | NOT NULL                               |
| seller_id   | INT            | FOREIGN KEY (references users.id)      |
| category_id | INT            | FOREIGN KEY (references categories.id) |

#### 3. 产品图片表 (product_images)

| 列名       | 数据类型     | 约束                                 |
| ---------- | ------------ | ------------------------------------ |
| id         | INT          | AUTO_INCREMENT, PRIMARY KEY          |
| product_id | INT          | FOREIGN KEY (references products.id) |
| image_url  | VARCHAR(255) | NOT NULL                             |

#### 4. 产品类别表 (categories)

| 列名 | 数据类型     | 约束                        |
| ---- | ------------ | --------------------------- |
| id   | INT          | AUTO_INCREMENT, PRIMARY KEY |
| name | VARCHAR(255) | UNIQUE, NOT NULL            |

#### 5. 购物车表 (carts)

| 列名       | 数据类型 | 约束                              |
| ---------- | -------- | --------------------------------- |
| id         | INT      | AUTO_INCREMENT, PRIMARY KEY       |
| user_id    | INT      | FOREIGN KEY (references users.id) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP         |

#### 6. 购物车项表 (cart_items)

| 列名       | 数据类型 | 约束                                 |
| ---------- | -------- | ------------------------------------ |
| id         | INT      | AUTO_INCREMENT, PRIMARY KEY          |
| cart_id    | INT      | FOREIGN KEY (references carts.id)    |
| product_id | INT      | FOREIGN KEY (references products.id) |
| quantity   | INT      | NOT NULL                             |

#### 7. 订单表 (orders)

| 列名             | 数据类型                                                | 约束                                |
|----------------|-----------------------------------------------------|-----------------------------------|
| id             | INT                                                 | AUTO_INCREMENT, PRIMARY KEY       |
| buyer_id       | INT                                                 | FOREIGN KEY (references users.id) |
| order_date     | DATETIME                                            | NOT NULL                          |
| status         | ENUM('pending', 'shipped', 'completed', 'canceled') | DEFAULT 'pending'                 |
| total_amount   | DECIMAL(10, 2)                                      | NOT NULL                          |
| status         | ENUM('pending', 'shipped', 'completed', 'canceled') | DEFAULT 'pending'                 |
| total_amount   | DECIMAL(10, 2)                                      | NOT NULL                          |
| recipient_name | VARCHAR(255)                                        | NOT NULL                          |
| phone          | VARCHAR(20)                                         | NOT NULL                          |
| address_line1  | VARCHAR(255)                                        | NOT NULL                          |
| address_line2  | VARCHAR(255)                                        |                                   |

#### 8. 已售产品表 (sold_products)

| 列名       | 数据类型   | 约束                                 |
| ---------- |----------| ------------------------------------ |
| id         | INT      | AUTO_INCREMENT, PRIMARY KEY          |
| seller_id  | INT      | FOREIGN KEY (references users.id)    |
| product_id | INT      | FOREIGN KEY (references products.id) |
| sold_date  | DATETIME | NOT NULL                             |
| quantity   | INT      | NOT NULL                             |

#### 9. 评论表 (reviews)

| 列名        | 数据类型 | 约束                                 |
| ----------- | -------- | ------------------------------------ |
| id          | INT      | AUTO_INCREMENT, PRIMARY KEY          |
| product_id  | INT      | FOREIGN KEY (references products.id) |
| user_id     | INT      | FOREIGN KEY (references users.id)    |
| rating      | INT      | NOT NULL (范围: 1-5)                 |
| comment     | TEXT     |                                      |
| review_date | DATETIME | DEFAULT CURRENT_TIMESTAMP            |

### 数据库关系说明

- **用户表 (users)**: 存储用户信息。
- **产品表 (products)**: 存储产品的基本信息。
- **产品图片表 (product_images)**: 每个产品可以关联多张图片，存储每张图片的URL。
- **产品类别表 (categories)**: 存储产品的类别，方便分类管理。
- **购物车表 (carts)**: 存储用户的购物车信息。
- **购物车项表 (cart_items)**: 存储购物车中的产品和数量。
- **订单表 (orders)**: 存储订单信息，记录用户购买的产品。
- **已售产品表 (sold_products)**: 存储卖出的产品信息。
- **评论表 (reviews)**: 存储用户对产品的评价。