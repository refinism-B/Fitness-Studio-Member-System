# 簡易會員管理系統

![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![Streamlit](https://img.shields.io/badge/GUI-Streamlit-red) ![Cloud](https://img.shields.io/badge/Deployment-Streamlit%20Cloud-orange) ![Database](https://img.shields.io/badge/Database-Google%20Sheets-green)

## 目錄（Menu）
- [簡介（Overview）](#簡介overview)
- [雲端部署（Cloud Deployment）](#雲端部署cloud-deployment)
- [技術與工具（Tech Stack）](#技術與工具tech-stack)
- [使用方式（Usage）](#使用方式usage)
- [資料庫（Database）](#資料庫database)
- [系統功能（System Functions）](#系統功能system-functions)

---

## 簡介（Overview）
本專案目的為建立一個小型、易用的資料庫系統，管理會員資料及記錄會員活動。並使用Python開發後端功能操作資料庫，將繁瑣的流程簡化，節省文書工作時間。
除了可於地端執行外，本專案已優化為**可部署至 Streamlit Cloud** 的版本，方便多裝置存取使用。

<br>

## 雲端部署（Cloud Deployment）
本專案已支援雲端部署，透過 Streamlit Cloud 託管應用程式，並連接 Google Sheets 作為雲端資料庫。
使用者僅需透過網頁連結即可操作，無須在地端安裝任何軟體或環境。

- **線上試用連結**：[https://fitness-studio-member-system.streamlit.app/](https://fitness-studio-member-system.streamlit.app/)

<br>

## 技術與工具（Tech Stack）
- 程式語言：**Python**
- 資料庫：**Google Sheets**
- GUI：**Streamlit**
- 部署環境：**Streamlit Cloud Community**

<br>

## 使用方式（Usage）
### 雲端版本
直接點擊 Streamlit Cloud 提供的應用程式連結即可開始使用：[健身訓練會員系統](https://fitness-studio-member-system.streamlit.app/)

### 地端開發/測試（Local Development）
若需在地端開發或測試：
1. 下載專案 repository。
2. 準備 `.streamlit/secrets.toml` 文件並配置 Google Sheets API 憑證。
3. 使用 `pip install -r requirements.txt` 安裝依賴套件。
4. 執行 `streamlit run streamlit_app.py` 啟動服務。

<br>

## 資料庫（Database）
本專案改用 **Google Sheets** 作為雲端資料庫，方便即時查看與協作。

- **測試資料庫連結**：[Google Sheets 範例](https://docs.google.com/spreadsheets/d/11bQVn6ioxgdsAsXSq8yfG-9EMBvBGS852gkK9nnvRQo/edit?usp=sharing)
  > **注意**：此為測試檢視連結，所有人均可查看資料變動（例如透過系統新增會員後，此表會即時更新），但無權限直接編輯試算表。

- **資料庫架構**：將 Google Sheet 的分頁（Sheets）視為 Tables 操作：
    1. **A_main**：會員結算資料，查看剩餘堂數與金額。每次異動自動更新。
    2. **B_event**：會員活動記錄（購買、上課、退費）。
    3. **C_member**：會員基本資料。
    4. **menu**：課程價目表（靜態設定）。
    5. **coach**：教練名單（靜態設定）。

- **注意事項**：系統操作會同步寫入此 Google Sheet。為避免資料不一致，建議主要透過本系統介面進行資料增刪改，而非直接編輯試算表。

<br>

## 系統功能（System Functions）
以下分為**主要功能**與**其他功能**介紹：

### 主要功能

**1. 新增會員**：在使用其他功能前，**務必將目標對象加入會員**。系統會驗證目標對象是否已是會員，若非會員則無法使用其他功能。且必須設定**會員編號**，此為每個會員獨有、不重複的ID，用以識別會員身分。

![新增會員](https://i.meee.com.tw/Y0611SE.png)
<br>

**2. 購買課程**：系統採用「**先買後用**」的消費機制。會員必須先購買一定數量的課程，才能使用（上課）。課程又分為兩類：
- **一般課程**：共有三種方案、四種堂數可選，金額皆為固定。
- **特殊課程**：堂數與單堂金額可任意輸入，提供客製化的購課方案。

![購買一般課程](https://i.meee.com.tw/OftB2Um.png)
![購買特殊課程](https://i.meee.com.tw/RakiGmv.png)
![重複確認](https://i.meee.com.tw/mAKhZHa.png)
<br>

**3. 會員上課**：可批量選取多位會員後執行，系統會將所有會員堂數`-1`。若會員剩餘堂數已經為0，系統會提醒並拒絕存取。*（建議上課前輸入，避免上完課才發現已無剩餘堂數）*

![會員上課](https://i.meee.com.tw/BfXHLo6.png)
<br>

**4. 庫存結算**：在每次會員資料異動時（購課或上課）系統會自動結算，按照**會員編號**及**方案**計算每位會員的剩餘堂數及款項，並更新至資料庫。

![結算](https://i.meee.com.tw/aEGny7G.png)
<br>


### 其他功能

- **手動更新**：點擊「手動更新」按鈕，系統會重新從 Google Sheets 讀取所有交易與會員紀錄，重新計算並覆寫主表（A_main）。當有人直接修改了 Google Sheets 內容後，可利用此功能強制同步系統狀態。
- **會員退款**：輸入會員編號及方案後會查詢剩餘堂數與金額，若確認退款，系統會新增一筆資料，**將該會員該方案的堂數與金額都扣除（歸零）**。

![會員退款](https://i.meee.com.tw/ECuH0Ug.png)
<br>

- **管理員權限**：在介面首頁可以輸入管理員密碼開啟權限。若登入為管理員，在各頁面均可**快速查看當前會員結算情形**。非管理員仍可使用各項功能，只是無法直接查看會員資料。

![登入系統](https://i.meee.com.tw/ADbUnNL.png)
<br>

> **注意**：雲端版本因環境限制，已移除**自動備份至本地**的功能。Google Sheets 本身即具備版本紀錄（History），可隨時還原至先前的狀態。

<br>

## 補充（Notes）
關於詳細程式架構請參考專案目錄中`docs`資料夾下的`專案架構說明書.md`檔案。
