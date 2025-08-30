import UserProfile from "@/components/auth/user-profile";
export default function SettingsPage() {
  return (
    <div className="settings-page">
      <h1>设置页面</h1>
      <p>这是设置页面的演示内容。</p>
      <UserProfile />
      <div className="settings-content">
        <div className="setting-item">
          <label>用户名:</label>
          <input type="text" placeholder="请输入用户名" />
        </div>
        <div className="setting-item">
          <label>邮箱:</label>
          <input type="email" placeholder="请输入邮箱地址" />
        </div>
        <div className="setting-item">
          <label>通知设置:</label>
          <input type="checkbox" id="notifications" />
          <label htmlFor="notifications">启用通知</label>
        </div>
        <button className="save-button">保存设置</button>
      </div>
    </div>
  );
}
