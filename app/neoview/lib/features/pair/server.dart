part of '../pair.dart';

abstract final class PythonServer {
  static final HttpClient client = HttpClient();

  static String _host = "localhost:8080";
  static Uri _uri = Uri.http(_host);

  static String get host => _host;
  static Uri get uri => _uri;

  static Future<ServerResult> _readText() async { throw UnimplementedError(); }
  static Future<ServerResult> _readAmbient() async { throw UnimplementedError(); }
  static Future<ServerResult> _mapTactileFloor() async { throw UnimplementedError(); }
  static Future<ServerResult> _ping() async {
    final result = await _pingUri(_uri);
    return result.statusCode == 200
      ? Success(result)
      : Failure("Não foi possível conectar ao servidor no host $_host");
  }

  static Future<Result<void, String>> setHost(String newHost) async {
    final response = await _pingUri(Uri.http(newHost));
    if (response.statusCode == 200) {
      _host = newHost;
      _uri = uri;
      return Success(null);
    } else {
      return Failure("Não foi possível conectar ao servidor no host $newHost");
    }
  }

  static Future<HttpClientResponse> _pingUri(Uri uri) async {
    final request = await client.getUrl(uri.replace(path: GlassesFunctionality.ping.endpoint));
    final response = await request.close();
    return response;
  }
}

typedef ServerResult = Result<HttpClientResponse, String>;