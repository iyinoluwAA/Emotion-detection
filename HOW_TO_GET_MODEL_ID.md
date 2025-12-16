# How to Get Your HuggingFace Model ID

## Quick Steps

### 1. Create Repository on HuggingFace

1. **Go to**: https://huggingface.co/new
2. **Select**: "Model" (the first option)
3. **Repository name**: Enter `asripa-emotion-detection`
4. **Visibility**: Choose "Public" (free) or "Private"
5. **Click**: "Create repository"

### 2. Find Your Model ID

After creating, you'll see a URL like:
```
https://huggingface.co/your-username/asripa-emotion-detection
```

Your **Model ID** is: `your-username/asripa-emotion-detection`

### 3. Examples

- If your username is `iyinoluwAA`:
  - Model ID: `iyinoluwAA/asripa-emotion-detection`

- If your username is `john-doe`:
  - Model ID: `john-doe/asripa-emotion-detection`

### 4. Use It

When the upload script asks:
```
Enter your HuggingFace model ID (e.g., username/asripa-emotion-detection):
```

Paste your model ID (e.g., `iyinoluwAA/asripa-emotion-detection`)

## Can't Find Your Username?

1. Go to: https://huggingface.co/settings/profile
2. Your username is shown at the top
3. Or check the URL when you're logged in - it shows in the navigation

## What Happens Next?

After you create the repository and get the model ID:
1. Run the upload script
2. Enter your model ID
3. The script will upload your 328MB Asripa model
4. Then set `ASRIPA_MODEL_ID` in Railway with the same value

