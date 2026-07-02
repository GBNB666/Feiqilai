import { useEffect, useState } from "react";
import { api } from "../../services/api";
import type { TemplateInfo } from "../../types";

interface Props {
  onSelect?: (template: TemplateInfo) => void;
}

export default function TemplateManager({ onSelect }: Props) {
  const [templates, setTemplates] = useState<TemplateInfo[]>([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    const data = await api.getTemplates();
    setTemplates(data);
  };

  useEffect(() => { load(); }, []);

  const save = async () => {
    if (!name.trim()) return;
    setLoading(true);
    await api.saveTemplate(name.trim(), JSON.stringify({}));
    setName("");
    setLoading(false);
    load();
  };

  const remove = async (id: number) => {
    await api.deleteTemplate(id);
    load();
  };

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-700">格式模板</h3>
      <div className="flex gap-2">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="模板名称"
          className="text-sm border rounded-lg px-3 py-1.5 flex-1"
        />
        <button
          onClick={save}
          disabled={loading || !name.trim()}
          className="text-sm px-4 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          保存
        </button>
      </div>
      <div className="space-y-1">
        {templates.map((t) => (
          <div
            key={t.id}
            className="flex items-center justify-between text-sm py-1.5 px-2 rounded hover:bg-gray-50"
          >
            <button
              onClick={() => onSelect?.(t)}
              className="text-indigo-700 hover:underline text-left"
            >
              {t.name}
            </button>
            {t.name !== "系统默认" && (
              <button
                onClick={() => remove(t.id)}
                className="text-red-400 hover:text-red-600 text-xs"
              >
                删除
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
