export const number = (value: number, digits = 0) => new Intl.NumberFormat("vi-VN", { maximumFractionDigits: digits }).format(value);
export const percent = (value: number) => `${number(value * 100, 1)}%`;
export function duration(seconds: number | null) {
  if (seconds === null) return "Chưa xác định";
  if (seconds <= 0) return "Đã chạm bình cảnh";
  if (seconds < 60) return `${Math.ceil(seconds)} giây`;
  const minutes = Math.ceil(seconds / 60);
  const hours = Math.floor(minutes / 60);
  return hours ? `${hours} giờ${minutes % 60 ? ` ${minutes % 60} phút` : ""}` : `${minutes} phút`;
}
export const elementNames: Record<string, string> = { metal: "Kim", wood: "Mộc", water: "Thủy", fire: "Hỏa", earth: "Thổ", ice: "Băng", lightning: "Lôi", wind: "Phong" };
export const qualityNames: Record<string, string> = { common: "Phổ thông" };
