# http-proxy

소켓으로 구현한 proxy입니다.

## 1. 구현 목표는 다음과 같다.

1. telnet을 이용해 내 프록시에 접근한다.

2. telnet쪽에서 send 명령어를 통해 보낸 HTTP 요청을 적절히 가공하여 본래의 서버로 대신 요청한다.

3. 본래의 서버로부터 받은 응답 패킷을 프록시에 캐싱한 후 telnet측에 대신 응답한다.

4. 이후 telnet측으로부터 동일한 요청을 받았을 시 본래의 서버로 요청을 넘기지 않고 즉시 캐시 데이터를 전달한다.

 

## 2. 이를 위해 고안한 메커니즘은 다음과 같다.

1. 사용자로부터 요청 패킷을 받을 서버 소켓을 만든다.

2. 전달받은 요청 패킷을 디코딩한 후, 본래의 서버로 전달하기 적절한 형태로 가공해준다.

3. 본래의 서버로 요청 패킷을 전송할 클라이언트 소켓을 만든다.

4. 가공한 패킷을 인코딩하여 본래의 서버로 전달한다.

5. 전달받은 응답 패킷을 디코딩한 후, URL과 페이로드를 매칭하여 캐싱한다.

6. 응답 패킷을 인코딩한 후 사용자에게 전달한다.

 

## 3. 추가적으로 구현한 사항은 다음과 같다.

1. 프록시 프로그램 실행 시 옵션으로 포트 번호를 지정할 수 있도록 한다.

2. 유효하지 않은 요청을 받았을 시 Bad Request로 응답한다.

3. GET 이외의 요청을 받았을 시 Not Implemented로 응답한다.

4. Selectors를 사용하여 소켓 멀티플렉싱을 구현한다.



## 4. 참고

소켓 멀티플렉싱 구현 전/후의 최종 스크립트를 모두 첨부한다.

▶ 소켓 멀티플렉싱을 구현하지 않은 스크립트가 가독성이 훨씬 높기 때문에 흐름 파악에 적절하다.
