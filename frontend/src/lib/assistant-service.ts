/**
 * VoiceOps Assistant Service
 * Handles communication with the assistant.py backend API
 */

const ASSISTANT_API_BASE = process.env.NEXT_PUBLIC_ASSISTANT_API_URL || 'http://127.0.0.1:5001';

export interface VoiceCommandResponse {
  success: boolean;
  command?: string;
  intent?: string;
  response?: string;
  actions?: Array<{
    device: string;
    command: string;
    value?: unknown;
  }>;
  firebase_success?: boolean;
  timestamp?: string;
  error?: string;
}

export interface AssistantHealthStatus {
  status: string;
  service: string;
  timestamp: string;
  firebase_connected: boolean;
  whisper_loaded: boolean;
  tts_available: boolean;
}

class AssistantService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = ASSISTANT_API_BASE;
  }

  /**
   * Check if the assistant service is running and healthy
   */
  async checkHealth(): Promise<AssistantHealthStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Assistant health check failed:', error);
      throw new Error('Assistant service is not available');
    }
  }

  /**
   * Process a text command through the assistant
   */
  async processTextCommand(
    command: string,
    speakResponse: boolean = false
  ): Promise<VoiceCommandResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/voice/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: command.trim(),
          speak_response: speakResponse,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Request failed: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('Text command processing failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  /**
   * Start voice listening for a specified duration
   */
  async listenForVoiceCommand(
    duration: number = 3,
    speakResponse: boolean = false
  ): Promise<VoiceCommandResponse> {
    try {
      // Ensure duration is within bounds
      duration = Math.max(1, Math.min(duration, 10));

      const response = await fetch(`${this.baseUrl}/api/voice/listen`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          duration,
          speak_response: speakResponse,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Request failed: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('Voice listening failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Voice listening failed',
      };
    }
  }

  /**
   * Control a device directly
   */
  async controlDevice(
    device: string,
    command: string,
    value?: unknown
  ): Promise<VoiceCommandResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/devices/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device,
          command,
          value,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Request failed: ${response.status}`);
      }

      return {
        success: data.success,
        command: `${device} ${command}`,
        intent: 'device_control',
        response: `${device} turned ${command}`,
        actions: [{ device, command, value }],
        firebase_success: data.success,
        timestamp: data.timestamp,
      };
    } catch (error) {
      console.error('Device control failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Device control failed',
      };
    }
  }

  /**
   * Check if the assistant service is available
   */
  async isServiceAvailable(): Promise<boolean> {
    try {
      await this.checkHealth();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get optimal listening duration based on command type
   */
  getOptimalDuration(commandType: 'short' | 'medium' | 'long' = 'medium'): number {
    switch (commandType) {
      case 'short':
        return 2; // For simple commands like "turn on light"
      case 'medium':
        return 4; // For normal commands
      case 'long':
        return 6; // For complex commands or questions
      default:
        return 3;
    }
  }

  /**
   * Format response for display
   */
  formatResponse(response: VoiceCommandResponse): string {
    if (!response.success) {
      return response.error || 'Command failed';
    }

    if (response.response) {
      return response.response;
    }

    if (response.actions && response.actions.length > 0) {
      const actionSummary = response.actions
        .map(action => `${action.device} ${action.command}`)
        .join(', ');
      return `Executed: ${actionSummary}`;
    }

    return 'Command processed successfully';
  }

  /**
   * Get intent display name
   */
  getIntentDisplayName(intent?: string): string {
    switch (intent) {
      case 'device_control':
        return 'Device Control';
      case 'sensor_query':
        return 'Sensor Query';
      case 'emergency':
        return 'Emergency';
      case 'password_access':
        return 'Access Control';
      case 'general_chat':
        return 'General Chat';
      case 'unknown':
        return 'Unknown Command';
      default:
        return 'Processing...';
    }
  }
}

// Export singleton instance
export const assistantService = new AssistantService();
export default assistantService; 