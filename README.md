# weibo2misskey
 A tool designed to clone and mirror selected Weibo bloggers' posts to a Misskey instance.


用于克隆微博到Misskey实例上的一个项目，参考了[weibo2mast](https://github.com/casouri/weibo2mast),[weibo-crawler](https://github.com/dataabc/weibo-crawler)，在Misskey上的api中创建一个启用全部权限的访问令牌粘贴到config.json中的misskey_token处,其余配置可自行修改。
```
include_repost: 是否包括用户转发的微博。如果设置为 true，则包括用户的转发内容；如果为 false，则只包括用户自己的原创微博。

standalone_repost: 当为 true 时，转发的微博将作为一个独立的帖子发布到 Misskey，而不是作为原始微博的评论。

include_post_url: 是否在转发到 Misskey 的帖子中包括原始微博的 URL。

misskey_instance_url: 你的 Misskey 实例的 URL。

misskey_token: 用于访问你的 Misskey 实例的访问令牌。

max_attachment_count: 在转发到 Misskey 的帖子中，可以包含的附件（例如图片或视频）的最大数量。

original_pic_download 和 retweet_pic_download: 是否下载原创微博和转发微博中的图片。1 表示下载，0 表示不下载。

original_video_download 和 retweet_video_download: 是否下载原创微博和转发微博中的视频。1 表示下载，0 表示不下载。

write_mode: 指定如何保存微博数据。默认情况数据将保存为 CSV 文件。

since_date: 只抓取此日期之后的微博。

delete_after_days: 在 Misskey 上发表的微博在指定的天数后将被删除。
filter: 为0时代码会检查微博是否为转发的，如果是，它将从原始微博中提取信息并为这些信息添加前缀 'retweet_'。同时，它会添加一个字段 'is_original' 来表示这条微博是否为原创。
```
推荐使用screen运行
