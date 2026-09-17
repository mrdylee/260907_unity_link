export type RackStatus = 'normal' | 'warning';

export interface RackTelemetry {
  rackId: number;
  temperatureC: number;
  voltageV: number;
  socPercent: number;
  sohPercent: number;
  currentA: number;
  state: 'CHARGING' | 'IDLE';
  status: RackStatus;
  diagnosticCode: 'NORMAL' | 'OVER_TEMPERATURE';
  diagnosticMessage: string;
}

export interface TelemetryProvider {
  readonly source: 'simulation' | 'modbus';
  read(): Promise<RackTelemetry[]>;
}

export interface EquipmentTelemetry {
  id: 'LCS' | 'eBSC';
  communication: 'ONLINE' | 'OFFLINE';
  mode: string;
  dsState?: 'OPEN' | 'CLOSED';
  diagnosticCode: 'NORMAL';
  diagnosticMessage: string;
}

export function telemetryStatus(temperatureC: number): RackStatus {
  return temperatureC >= 35 ? 'warning' : 'normal';
}

export function formatRackLabel(rackId: number): string {
  return `RACK ${String(rackId).padStart(2, '0')}`;
}

const sampleValues = [
  [27.4, 768.2, 82],
  [28.1, 766.8, 79],
  [29.6, 769.5, 85],
  [36.2, 764.1, 72],
  [30.3, 767.7, 77],
  [26.9, 770.0, 88],
] as const;

export class SampleTelemetryProvider implements TelemetryProvider {
  readonly source = 'simulation' as const;

  async read(): Promise<RackTelemetry[]> {
    return sampleValues.map(([temperatureC, voltageV, socPercent], index) => ({
      rackId: index + 1,
      temperatureC,
      voltageV,
      socPercent,
      sohPercent: 98 - index * 0.3,
      currentA: index === 3 ? 0 : 24.5 + index,
      state: index === 3 ? 'IDLE' : 'CHARGING',
      status: telemetryStatus(temperatureC),
      diagnosticCode: temperatureC >= 35 ? 'OVER_TEMPERATURE' : 'NORMAL',
      diagnosticMessage: temperatureC >= 35 ? '랙 내부 온도 상한 초과' : '진단 이상 없음',
    }));
  }

  async readEquipment(): Promise<EquipmentTelemetry[]> {
    return [
      { id: 'LCS', communication: 'ONLINE', mode: 'AUTO', dsState: 'CLOSED', diagnosticCode: 'NORMAL', diagnosticMessage: '랙 데이터 수집 정상' },
      { id: 'eBSC', communication: 'ONLINE', mode: 'MONITORING', diagnosticCode: 'NORMAL', diagnosticMessage: 'LAN 4채널 통신 정상' },
    ];
  }
}
