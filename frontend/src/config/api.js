/**
 * NavAI - API Service
 * Handles all communication with the FastAPI backend.
 */
import API_CONFIG from "../config/api";

class NavAIService {
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  async checkHealth() {
    try {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), 5000);
      const res = await fetch(`${this.baseUrl}/`, { signal: controller.signal });
      clearTimeout(id);
      const data = await res.json();
      return data.status === "online";
    } catch (e) {
      console.error("Health check failed:", e.message);
      return false;
    }
  }

  async processQuery(imageUri, question) {
    const formData = new FormData();
    formData.append("image", { uri: imageUri, type: "image/jpeg", name: "capture.jpg" });
    formData.append("question", question);

    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), this.timeout);

    const res = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.PROCESS}`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
    clearTimeout(id);
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    return await res.json();
  }

  async detectObjects(imageUri) {
    const formData = new FormData();
    formData.append("image", { uri: imageUri, type: "image/jpeg", name: "capture.jpg" });
    const res = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.DETECT}`, {
      method: "POST",
      body: formData,
    });
    return await res.json();
  }

  async extractText(imageUri) {
    const formData = new FormData();
    formData.append("image", { uri: imageUri, type: "image/jpeg", name: "capture.jpg" });
    const res = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.OCR}`, {
      method: "POST",
      body: formData,
    });
    return await res.json();
  }

  async getAnswer(question, context) {
    const formData = new FormData();
    formData.append("question", question);
    formData.append("context", context);
    const res = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.QNA}`, {
      method: "POST",
      body: formData,
    });
    return await res.json();
  }
}

export default new NavAIService();
