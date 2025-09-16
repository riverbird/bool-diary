fpm -s dir -t deb -n booldiary -v 0.1.0 --description "Your diary App." \
	--maintainer "Hunter Zhang <riverbird@aliyun.com>" \
	--architecture amd64 \
	-C /home/riverbird/project/bool-diary-mobile-2/build/linux \
	.=usr/local/bool-diary \
	bool-diary.desktop=/usr/share/applications/bool-diary.desktop
