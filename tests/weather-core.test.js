'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const weather = require('../scripts/weather-core.js');

const cities = [
  { name: '杭州', lat: 30.27, lon: 120.15 },
  { name: '大连', lat: 38.91, lon: 121.61 },
];

function response(city = cities[0], daily = {}) {
  return {
    latitude: city.lat,
    longitude: city.lon,
    timezone: 'Asia/Shanghai',
    daily_units: {
      temperature_2m_max: '°C',
      temperature_2m_min: '°C',
      wind_speed_10m_max: 'km/h',
      wind_gusts_10m_max: 'km/h',
      wind_direction_10m_dominant: '°',
      precipitation_probability_max: '%',
      precipitation_sum: 'mm',
    },
    daily: {
      time: ['2026-09-27'],
      temperature_2m_min: [18.3],
      temperature_2m_max: [25.7],
      weather_code: [3],
      precipitation_probability_max: [null],
      precipitation_sum: [null],
      wind_speed_10m_max: [null],
      wind_gusts_10m_max: [null],
      wind_direction_10m_dominant: [null],
      ...daily,
    },
  };
}

test('missing optional values remain null rather than 0 or north wind', () => {
  const result = weather.forecast(response(), '2026-09-27', '2026-09-20');
  assert.equal(result.available, true);
  assert.equal(result.low, 18);
  assert.equal(result.high, 26);
  for (const field of ['rain', 'rainMM', 'wind', 'gust']) assert.equal(result[field], null);
  assert.equal(result.direction, '风向待更新');
  assert.equal(weather.finite(null), false);
  assert.equal(weather.finite('0'), false);
  assert.equal(weather.finite(0), true);
});

test('missing required weather values do not become a 0 degree sunny forecast', () => {
  for (const field of ['temperature_2m_min', 'temperature_2m_max', 'weather_code']) {
    const result = weather.forecast(response(cities[0], { [field]: [null] }), '2026-09-27', '2026-09-20');
    assert.deepEqual(result, { available: false, past: false });
  }
});

test('forecast matches the exact YYYY-MM-DD date even when response dates are out of order', () => {
  const payload = response(cities[0], {
    time: ['2026-10-01', '2026-09-27', '2026-09-28'],
    temperature_2m_min: [10, 18, 20],
    temperature_2m_max: [15, 26, 30],
    weather_code: [61, 3, 0],
  });
  const result = weather.forecast(payload, '2026-09-27', '2026-09-20');
  assert.equal(result.low, 18);
  assert.equal(result.high, 26);
  assert.equal(result.text, '阴');
  assert.deepEqual(weather.forecast(payload, '2026-10-07', '2026-09-20'), { available: false, past: false });
});

test('a past trip date is not presented as a future forecast, even if included in the payload', () => {
  assert.deepEqual(weather.forecast(response(), '2026-09-27', '2026-09-28'), { available: false, past: true });
  assert.equal(weather.forecast(response(), '2026-09-27', '2026-09-27').available, true);
});

test('trend begins at seven days ahead; day six remains a nearer forecast', () => {
  assert.equal(weather.forecast(response(), '2026-09-27', '2026-09-21').trend, false);
  assert.equal(weather.forecast(response(), '2026-09-27', '2026-09-20').trend, true);
});

test('a zero-degree temperature and WMO clear-sky code 0 remain valid', () => {
  const result = weather.forecast(response(cities[0], {
    temperature_2m_min: [0], temperature_2m_max: [8], weather_code: [0],
  }), '2026-09-27', '2026-09-27');
  assert.equal(result.available, true);
  assert.equal(result.low, 0);
  assert.equal(result.text, '晴');
});

test('validate rejects wind speed in m/s instead of the requested km/h', () => {
  const payload = cities.map(city => response(city));
  assert.equal(weather.validate(payload, cities), payload);
  payload[1].daily_units.wind_speed_10m_max = 'm/s';
  assert.throws(() => weather.validate(payload, cities), /天气单位不匹配/);
});

test('validate rejects reversed city order or mismatched coordinates and timezone', () => {
  assert.throws(() => weather.validate([response(cities[1]), response(cities[0])], cities), /城市或时区不匹配/);
  const payload = cities.map(city => response(city));
  payload[1].longitude += 1;
  assert.throws(() => weather.validate(payload, cities), /城市或时区不匹配/);
  payload[1] = response(cities[1]);
  payload[1].timezone = 'UTC';
  assert.throws(() => weather.validate(payload, cities), /城市或时区不匹配/);
});

test('validate rejects incomplete city arrays and required daily arrays', () => {
  assert.throws(() => weather.validate([response()], cities), /城市数据不完整/);
  const payload = cities.map(city => response(city));
  payload[1].daily.weather_code = [];
  assert.throws(() => weather.validate(payload, cities), /天气字段不完整/);
});

test('rain code or substantial rain probability adds waterproof clothing and dry socks', () => {
  const base = { available: true, low: 16, high: 24, code: 3, rain: null, wind: null, gust: null };
  assert.doesNotMatch(weather.clothing([base]), /带防雨外层和干袜/);
  assert.match(weather.clothing([{ ...base, code: 61 }]), /带防雨外层和干袜/);
  assert.match(weather.clothing([{ ...base, rain: 40 }]), /带防雨外层和干袜/);
  assert.match(weather.clothing([{ ...base, low: 10, wind: 25 }]), /保暖中层.*缩短海边停留/);
});

test('clothing combines transfer-day cities and explicitly retains layers for missing city data', () => {
  const advice = weather.clothing([
    { available: true, low: 20, high: 30, code: 0, rain: 0 },
    { available: true, low: 10, high: 18, code: 61, rain: 80 },
    { available: false },
  ]);
  assert.match(advice, /透气薄上衣/);
  assert.match(advice, /保暖中层/);
  assert.match(advice, /带防雨外层和干袜/);
  assert.match(advice, /另一地点仍待预报/);
  assert.match(weather.clothing([{ available: false }]), /预报尚未完整发布/);
});

test('multi-city API URL preserves coordinate order and explicitly requests Shanghai dates and units', () => {
  const url = new URL(weather.buildURL(cities));
  assert.equal(url.origin + url.pathname, 'https://api.open-meteo.com/v1/forecast');
  assert.equal(url.searchParams.get('latitude'), '30.27,38.91');
  assert.equal(url.searchParams.get('longitude'), '120.15,121.61');
  assert.equal(url.searchParams.get('timezone'), 'Asia/Shanghai');
  assert.equal(url.searchParams.get('forecast_days'), '16');
  assert.equal(url.searchParams.get('wind_speed_unit'), 'kmh');
  assert.equal(url.searchParams.get('temperature_unit'), 'celsius');
  assert.equal(url.searchParams.get('precipitation_unit'), 'mm');
  assert.deepEqual(url.searchParams.get('daily').split(','), [
    'weather_code', 'temperature_2m_max', 'temperature_2m_min',
    'precipitation_probability_max', 'precipitation_sum',
    'wind_speed_10m_max', 'wind_gusts_10m_max', 'wind_direction_10m_dominant',
  ]);
});

test('China date uses Shanghai midnight rather than the browser UTC day', () => {
  assert.equal(weather.chinaDate(new Date('2026-09-26T15:59:59Z')), '2026-09-26');
  assert.equal(weather.chinaDate(new Date('2026-09-26T16:00:00Z')), '2026-09-27');
});
