#!/usr/bin/env bash  

if [[ "$DEBUG" == "true" ]]; then
  set -x
fi

test_canu_version_using_docker() {
  local image="${1:-canu}"
  local version="${2:-latest}"
  docker run -it --rm --net=host "${image}":"${version}" canu --version
}

test_canu_version_using_canud() {
  local image="${1:-canu}"
  local version="${2:-latest}"
  ./canud -i "${image}":"${version}" canu --version
}

test_canu_validate_paddle_using_docker() {
  local image="${1:-canu}"
  local version="${2:-latest}"
  docker run -it --rm --net=host -v "${PWD}":/home/canu/mounted "${image}":"${version}" canu validate paddle --ccj mounted/tests/data/Full_Architecture_Golden_Config_1.1.5.json
}

test_canu_validate_shcd_tds_using_docker() {
  local image="${1:-canu}"
  local version="${2:-latest}"
  docker run -it --rm --net=host -v "${PWD}":/home/canu/mounted "${image}":"${version}" \
    canu validate shcd \
    --shcd mounted/tests/data/TDS_Architecture_Golden_Config_1.1.5.xlsx \
    --tabs SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES \
    --corners J14,T30,J14,T53,J14,T32,J14,T27 \
    --architecture TDS
}

test_canu_validate_shcd_tds_using_canud() {
  local image="${1:-canu}"
  local version="${2:-latest}"
  ./canud -i "${image}":"${version}" \
    canu validate shcd \
    --shcd mounted/tests/data/TDS_Architecture_Golden_Config_1.1.5.xlsx \
    --tabs SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES \
    --corners J14,T30,J14,T53,J14,T32,J14,T27 \
    --architecture TDS
}

test_canu_validate_shcd_full_make_paddle_using_docker() {
  local image="${1:-canu}"
  local version="${2:-latest}"
  docker run -it --rm --net=host -v "${PWD}":/home/canu/mounted "${image}":"${version}" \
    canu validate shcd \
    --shcd mounted/tests/data/Full_Architecture_Golden_Config_1.1.5.xlsx \
    --tabs SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES \
    --corners J14,T44,J14,T53,J14,T34,J14,T27 \
    --architecture Full \
    --out mounted/full_paddle.json \
    --json 
}

test_canu_validate_shcd_full_make_paddle_using_canud() {
  local image="${1:-canu}"
  local version="${2:-latest}"
  ./canud -i "${image}":"${version}" \
    canu validate shcd \
    --shcd mounted/tests/data/Full_Architecture_Golden_Config_1.1.5.xlsx \
    --tabs SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES \
    --corners J14,T44,J14,T53,J14,T34,J14,T27 \
    --architecture Full \
    --out mounted/full_paddle.json \
    --json 
}

OPTIND=1
while getopts "h?i:v:abcdefgj" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    i)  IMAGE=$OPTARG
        ;;
    v)  VERSION=$OPTARG
        ;;
    a)  test_canu_version_using_docker "$IMAGE" "$VERSION"
        ;;
    b)  test_canu_version_using_canud "$IMAGE" "$VERSION"
        ;;
    c)  test_canu_validate_paddle_using_docker "$IMAGE" "$VERSION"
        ;;
    d)  test_canu_validate_paddle_using_docker "$IMAGE" "$VERSION"
        ;;
    e)  test_canu_validate_shcd_tds_using_docker "$IMAGE" "$VERSION"
        ;;
    f)  test_canu_validate_shcd_tds_using_canud "$IMAGE" "$VERSION"
        ;;
    g)  test_canu_validate_shcd_full_make_paddle_using_docker "$IMAGE" "$VERSION"
        ;;
    j)  test_canu_validate_shcd_full_make_paddle_using_canud "$IMAGE" "$VERSION"
        ;;
    esac
done
shift $((OPTIND - 1))
