class VideoStatusStore {
  async get(id) {
    throw new Error('Not implemented');
  }

  async set(id, status) {
    throw new Error('Not implemented');
  }
}

const fs = require('fs');
const path = require('path');

class FileVideoStatusStore extends VideoStatusStore {
  constructor(filePath = path.join(__dirname, '..', 'video_statuses.json')) {
    super();
    this.filePath = filePath;
    this.store = new Map();
    this._load();
  }

  _load() {
    try {
      if (fs.existsSync(this.filePath)) {
        const raw = fs.readFileSync(this.filePath, 'utf8');
        const data = raw ? JSON.parse(raw) : {};
        this.store = new Map(Object.entries(data));
      }
    } catch (err) {
      console.error('Failed to load video status store', err);
    }
  }

  _save() {
    try {
      const obj = Object.fromEntries(this.store);
      fs.writeFileSync(this.filePath, JSON.stringify(obj, null, 2));
    } catch (err) {
      console.error('Failed to save video status store', err);
    }
  }

  async get(id) {
    return this.store.get(id) || null;
  }

  async set(id, status) {
    this.store.set(id, status);
    this._save();
  }
}

module.exports = { VideoStatusStore, FileVideoStatusStore };
