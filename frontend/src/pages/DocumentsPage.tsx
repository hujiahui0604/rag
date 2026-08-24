import { useState, useEffect } from 'react';
import { documentApi, categoryApi, Document, Category } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Header } from '../components/Header';
import { formatDate, formatFileSize } from '../lib/utils';
import { Upload, FileText, Search, Trash2, Loader2 } from 'lucide-react';

const STATUS_LABEL: Record<string, string> = {
  pending: '待索引',
  processing: '索引中',
  completed: '已完成',
  failed: '索引失败',
};

export function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [search, setSearch] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [uploadCategory, setUploadCategory] = useState<number | undefined>();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [docsRes, catsRes] = await Promise.all([
        documentApi.list(),
        categoryApi.list(),
      ]);
      setDocuments(docsRes.data.items);
      setCategories(catsRes.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const res = await documentApi.list({ search: search || undefined });
      setDocuments(res.data.items);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !uploadTitle) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('title', uploadTitle);
      if (uploadDescription) formData.append('description', uploadDescription);
      if (uploadCategory) formData.append('category_id', String(uploadCategory));

      const created = await documentApi.create(formData);
      setShowUpload(false);
      setUploadFile(null);
      setUploadTitle('');
      setUploadDescription('');

      // 上传后自动索引到向量库，使其可被 RAG 检索
      try {
        await documentApi.index(created.data.id);
      } catch (err) {
        console.error('Index failed:', err);
      }
      loadData();
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleReindex = async (id: number) => {
  setLoading(true);
  try {
    await documentApi.index(id);
    loadData();
  } catch (error) {
    console.error('Reindex failed:', error);
  } finally {
    setLoading(false);
  }
};

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个文档吗?')) return;
    try {
      await documentApi.delete(id);
      loadData();
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="container mx-auto py-8 px-4">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">文档管理</h1>
          <Button onClick={() => setShowUpload(true)}>
            <Upload className="h-4 w-4 mr-2" />
            上传文档
          </Button>
        </div>

        <div className="flex gap-4 mb-6">
          <div className="flex-1 flex gap-2">
            <Input
              placeholder="搜索文档..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button variant="outline" onClick={handleSearch}>
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            暂无文档，请上传第一个文档
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {documents.map((doc) => (
              <Card key={doc.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-muted-foreground" />
                      <CardTitle className="text-base">{doc.title}</CardTitle>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleReindex(doc.id)}
                        disabled={loading}
                      >
                        <Loader2 className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                        索引
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(doc.id)}
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                  <CardDescription>{doc.description || '无描述'}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>类型: {doc.file_type}</p>
                    <p>大小: {formatFileSize(doc.file_size)}</p>
                    <p>状态: {STATUS_LABEL[doc.status] || doc.status}</p>
                    <p>块数: {doc.chunk_count}</p>
                    <p>上传时间: {formatDate(doc.created_at)}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {showUpload && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md mx-4">
              <CardHeader>
                <CardTitle>上传文档</CardTitle>
                <CardDescription>支持 PDF, DOCX, TXT, MD 格式</CardDescription>
              </CardHeader>
              <form onSubmit={handleUpload}>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="file">选择文件</Label>
                    <Input
                      id="file"
                      type="file"
                      accept=".pdf,.docx,.txt,.md"
                      onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="title">标题</Label>
                    <Input
                      id="title"
                      value={uploadTitle}
                      onChange={(e) => setUploadTitle(e.target.value)}
                      placeholder="请输入文档标题"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">描述</Label>
                    <Input
                      id="description"
                      value={uploadDescription}
                      onChange={(e) => setUploadDescription(e.target.value)}
                      placeholder="可选描述"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="category">分类</Label>
                    <select
                      id="category"
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                      value={uploadCategory || ''}
                      onChange={(e) => setUploadCategory(e.target.value ? Number(e.target.value) : undefined)}
                    >
                      <option value="">选择分类</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </CardContent>
                <div className="flex justify-end gap-2 p-6">
                  <Button variant="outline" type="button" onClick={() => setShowUpload(false)}>
                    取消
                  </Button>
                  <Button type="submit" disabled={uploading}>
                    {uploading ? '上传中...' : '上传'}
                  </Button>
                </div>
              </form>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}