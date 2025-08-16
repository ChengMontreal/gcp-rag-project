#!/bin/bash

# ==============================================================================
# Environment Configuration for the RAG-on-GCP Project
# ==============================================================================
# 使用方法:
# 1. 将下面的 YOUR_GCP_PROJECT_ID_HERE 替换成你真实的 GCP 项目ID。
# 2. 在项目根目录下保存为 'setup_env.sh'。
# 3. 每次打开新终端时，运行 'source setup_env.sh' 来加载这些变量。
# ==============================================================================

# --- 1. 用户自定义配置 ---
# ‼️ 请务必替换成你自己的 Google Cloud 项目 ID。
export PROJECT_ID="rag-on"


# --- 2. GCP 基础设置 (通常无需修改) ---
export REGION="us-central1"
export ZONE="us-central1-a"


# --- 3. 服务账号名称 (通常无需修改) ---
export SERVICE_ACCOUNT_NAME="rag-app-sa"


# --- 4. 自动派生的变量 (请勿修改) ---
# 下面的变量会根据你上面填写的 PROJECT_ID 自动生成。
export SERVICE_ACCOUNT_ID="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
export BUCKET_NAME="rag-input-pdfs-${PROJECT_ID}" # 已更新为代码需要的名字


# --- 5. 在部署过程中创建的资源ID ---
# CORRECTED: These are the new IDs for your STREAM_UPDATE resources.
# 你的 Vertex AI Index ID:
export ME_INDEX_ID_VALUE="2729412271628353536"

# 你的 Vertex AI Index Endpoint ID:
export ME_INDEX_ENDPOINT_ID_VALUE="4719176474182025216"


# --- 6. 运行脚本时的确认信息 ---
echo "✅ 环境配置加载成功!"
echo "   - GCP 项目 ID: $PROJECT_ID"
echo "   - 区域: $REGION"
echo "   - 服务账号: $SERVICE_ACCOUNT_ID"
echo "   - GCS 存储桶: $BUCKET_NAME"
echo "   - Index ID: $ME_INDEX_ID_VALUE"
echo "   - Endpoint ID: $ME_INDEX_ENDPOINT_ID_VALUE"