function kakaoShare(num){
    Kakao.Share.sendDefault({
        objectType: 'feed',
        content: {
        title: '나와 닮은 개발자 찾기 결과',
        description: '정글러를 위한 심리테스트',
        imageUrl:
            'https://swjungle.net/static/image/big-icon.png',
        link: {
            mobileWebUrl: 'http://jungleptest.xyz/dev' + num,
            webUrl: 'http://jungleptest.xyz/dev' + num,
        },
        },
        buttons: [
        {
            title: '결과 확인하기',
            link: {
            webUrl: 'http://jungleptest.xyz/dev' + num,
            },
        },
        ],
    });
}
